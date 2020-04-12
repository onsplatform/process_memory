from util import convert_to_utc
from datetime import datetime

from flask_api import status
from flask import Blueprint, request, jsonify, make_response, current_app as app

from pymongo import ASCENDING
from bson.json_util import loads
from process_memory.db import get_database

bp = Blueprint('instances', __name__)


@bp.route("/<uuid:instance_id>/head")
def find_head(instance_id):
    entities, event, fork, maps, instance_filter = _get_memory_body(instance_id)
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
        result['instance_filter'] = instance_filter if instance_filter else []

        return jsonify(result)
    return make_response('', status.HTTP_404_NOT_FOUND)


def _get_memory_body(instance_id):
    event = _get_event_body(instance_id)
    maps = _get_maps(instance_id)
    entities = _get_entities(instance_id)
    fork = get_memory_part(instance_id, 'fork')
    instance_filter = _get_instance_filter(instance_id)
    return entities, event, fork, maps, instance_filter


def _get_event_body(instance_id):
    event = get_memory_part(instance_id, 'event')
    if event['referenceDate']:
        event['referenceDate'] = event['referenceDate'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return event


@bp.route('/entities/with/ids', methods=['POST'])
def get_entities_with_ids():
    if request.data:
        data = set()
        db = get_database()
        app.logger.debug('getting entities with ids:')
        for item in loads(request.data).pop('entities', None):
            app.logger.debug(item)
            query_items = {f"data.id": {"$eq": item['id']}}
            [data.add(item['header']['instanceId']) for item in db['entities'].find(query_items)]

        if data:
            return jsonify(
                [item['instanceId'] for item in
                 db['event'].find({
                     "instanceId": {"$in": list(data)},
                     'scope': {'$eq':'execution'}
                 }).sort('timestamp', ASCENDING)])

    return make_response('', status.HTTP_404_NOT_FOUND)


@bp.route("/entities/with/type", methods=['POST'])
def get_entities_with_type():
    if request.data:
        data = set()
        db = get_database()
        app.logger.debug('getting entities with type:')
        for item in loads(request.data).pop('entities', None):
            app.logger.debug(item)
            query_items = {f"type": {"$eq": item['type']}}
            [data.add(item['header']['instanceId']) for item in db['entities'].find(query_items)]

        if data:
            return jsonify(
                [item['instanceId'] for item in
                 db['event'].find({
                     "instanceId": {"$in": list(data)},
                     'scope': {'$eq':'execution'}
                 }).sort('timestamp', ASCENDING)])

    return make_response('', status.HTTP_404_NOT_FOUND)


@bp.route("/events/between/dates", methods=['POST'])
def get_events_between_dates():
    if request.data:
        db = get_database()
        json = loads(request.data)
        date_format = '%Y-%m-%dT%H:%M:%S.%f'
        date_begin_validity = convert_to_utc(json['date_begin_validity'], date_format)
        date_end_validity = convert_to_utc(datetime.now().strftime(date_format), date_format)
        process_id = json['process_id']
        if json['date_end_validity']:
            date_end_validity = convert_to_utc(json['date_end_validity'], date_format)

        app.logger.debug(f'getting events between dates {date_begin_validity} and {date_end_validity}')
        return jsonify(
            [item['instanceId'] for item in
             db['event'].find({
                 'referenceDate': {
                     '$gte': date_begin_validity,
                     '$lte': date_end_validity,
                 },
                 'header.processId': {"$eq": process_id},
                 'scope': {'$eq':'execution'}
             }).sort('referenceDate', ASCENDING)])

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
    return jsonify(_get_event_body(instance_id))


@bp.route("/entities/<uuid:instance_id>", methods=['GET'])
def get_entities(instance_id):
    return jsonify(_get_entities(instance_id))


@bp.route("/maps/<uuid:instance_id>", methods=['GET'])
def get_maps(instance_id):
    return jsonify(_get_maps(instance_id))

@bp.route("/instance_filter/<uuid:instance_id>", methods=['GET'])
def get_instance_filter(instance_id):
    return jsonify(_get_instance_filter(instance_id))


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


def _get_instance_filter(instance_id):
    header_query = {"header.instanceId": str(instance_id)}

    db = get_database()
    ret = []
    items = [item for item in db['instance_filter'].find(header_query)]
    for item in items:
        item.pop('_id')
        ret.append(item)

    return items