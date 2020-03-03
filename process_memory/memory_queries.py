import util
from datetime import datetime
from flask_api import status
from flask import Blueprint, request, jsonify, make_response
from pymongo import ASCENDING
from bson.json_util import loads
from process_memory.db import get_database

bp = Blueprint('instances', __name__)


@bp.route("/<uuid:instance_id>/head")
def find_head(instance_id):
    entities, event, fork, maps = _get_memory_body(instance_id)
    if event:
        result = dict()
        result['event'] = event if event else None
        result['map'] = {'content': maps if maps else {}, 'name': event['header']['app_name']}
        result['dataset'] = {'entities': entities if entities else {}}
        result['fork'] = fork if fork else None
        result['processId'] = result['event']['header']['processId']
        result['systemId'] = result['event']['header']['systemId']
        result['instanceId'] = result['event']['header']['instanceId']
        result['eventOut'] = result['event']['header']['eventOut']
        commit = result['event']['header']['commit']
        result['commit'] = commit if commit else False

        return jsonify(result)
    return make_response('', status.HTTP_404_NOT_FOUND)


def _get_memory_body(instance_id):
    event = get_memory_part(instance_id, 'event')
    maps = _get_maps(instance_id)
    entities = _get_entities(instance_id)
    fork = get_memory_part(instance_id, 'fork')
    return entities, event, fork, maps


@bp.route('/entities/with/ids', methods=['POST'])
def get_entities_with_ids():
    if request.data:
        data = set()
        db = get_database()
        for item in loads(request.data).pop('entities', None):
            query_items = {f"header.timestamp": {"$gte": util.get_datetime_from(item['timestamp'])},
                           f"data.id": {"$eq": item['id']}}
            [data.add(item['header']['instanceId']) for item in db['entities'].find(query_items)]
        if data:
            return jsonify(
                [item['instanceId'] for item in
                 db['event'].find({"instanceId": {"$in": list(data)}}).sort('timestamp', ASCENDING)])

    return make_response('', status.HTTP_404_NOT_FOUND)


@bp.route("/entities/with/type", methods=['POST'])
def get_entities_with_type():
    if request.data:
        data = set()
        db = get_database()

        for item in loads(request.data).pop('entities', None):
            query_items = {f"header.timestamp": {"$gte": util.get_datetime_from(item['timestamp'])},
                           f"type": {"$eq": item['type']}}
            [data.add(item['header']['instanceId']) for item in db['entities'].find(query_items)]

        if data:
            return jsonify(
                [item['instanceId'] for item in
                 db['event'].find({"instanceId": {"$in": list(data)}}).sort('timestamp', ASCENDING)])

    return make_response('', status.HTTP_404_NOT_FOUND)


def _format_timestamp(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')

@bp.route("/payload/<uuid:instance_id>", methods=['GET'])
def get_payload(instance_id):
    event = get_memory_part(instance_id, 'event')
    if event:
        return jsonify(event['payload'])

    return make_response('', status.HTTP_404_NOT_FOUND)


@bp.route("/fork/<uuid:instance_id>", methods=['GET'])
def get_fork(instance_id):
    return jsonify(get_memory_part(instance_id, 'fork'))


@bp.route("/event/<uuid:instance_id>", methods=['GET'])
def get_event(instance_id):
    return jsonify(get_memory_part(instance_id, 'event'))


@bp.route("/entities/<uuid:instance_id>", methods=['GET'])
def get_entities(instance_id):
    return jsonify(_get_entities(instance_id))


@bp.route("/maps/<uuid:instance_id>", methods=['GET'])
def get_maps(instance_id):
    return jsonify(_get_maps(instance_id))


def get_memory_part(instance_id, collection):
    header_query = {"header.instanceId": str(instance_id)}
    db = get_database()
    data = db[collection].find_one(header_query)
    if data:
        data.pop('_id')
        return data

def _get_maps(instance_id):
    header_query = {"header.instanceId": str(instance_id)}

    db = get_database()
    items = [item for item in db['maps'].find(header_query)]
    ret = dict()
    for item in items:
        ret[item['type']] = item['data']

    return ret

def _get_entities(instance_id):
    header_query = {"header.instanceId": str(instance_id)}

    db = get_database()
    items = [item for item in db['entities'].find(header_query)]
    ret = dict()
    for item in items:
        if not item['type'] in ret.keys():
            ret[item['type']] = []
        ret[item['type']].append(item['data'])

    return ret
