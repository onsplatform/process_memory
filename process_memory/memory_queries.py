from flask import Blueprint, request, jsonify
from pymongo import ASCENDING
from bson.json_util import loads
from process_memory.db import get_database

bp = Blueprint('instances', __name__)


@bp.route("/<uuid:instance_id>/head")
def find_head(instance_id):
    result = dict()
    event = get_event(instance_id)
    maps = get_maps(instance_id)
    entities = get_entities(instance_id)
    fork = get_fork(instance_id)

    result['event'] = loads(event.data) if event and event.data else None
    result['map'] = {'content': loads(maps.data) if maps and maps.data else None}
    result['dataset'] = {'entities': loads(entities.data) if entities and entities.data else None}
    result['fork'] = loads(fork.data) if fork and fork.data else None
    result['processId'] = result['event']['header']['processId']
    result['systemId'] = result['event']['header']['systemId']
    result['instanceId'] = result['event']['header']['instanceId']
    result['eventOut'] = result['event']['header']['eventOut']
    result['commit'] = result['event']['header']['commit']

    return jsonify(result)


@bp.route('/entities/with/ids', methods=['POST'])
def get_entities_with_ids():
    if request.data:
        data = set()
        db = get_database()

        for item in loads(request.data).pop('entities', None):
            query_items = {f"header.timestamp": {"$gte": item['timestamp']},
                           f"data.id": {"$eq": item['id']}}
            [data.add(item['header']['instanceId']) for item in db['entities'].find(query_items)]
        print(list(data))
        if data:
            return jsonify(
                [item['instanceId'] for item in
                 db['event'].find({"instanceId": {"$in": list(data)}}).sort('timestamp', ASCENDING)])


@bp.route("/entities/with/type", methods=['POST'])
def get_entities_with_type():
    if request.data:
        data = set()
        db = get_database()

        for item in loads(request.data).pop('entities', None):
            query_items = {f"header.timestamp": {"$gte": item['timestamp']},
                           f"type": {"$eq": item['type']}}
            [data.add(item['header']['instanceId']) for item in db['entities'].find(query_items)]

        if data:
            return jsonify(
                [item['instanceId'] for item in
                 db['event'].find({"instanceId": {"$in": list(data)}}).sort('timestamp', ASCENDING)])


@bp.route("/payload/<uuid:instance_id>", methods=['GET'])
def get_payload(instance_id):
    event = get_memory_part(instance_id, 'event')
    if event and event.data:
        return loads(event.data)['payload']


@bp.route("/fork/<uuid:instance_id>", methods=['GET'])
def get_fork(instance_id):
    return get_memory_part(instance_id, 'fork')


@bp.route("/event/<uuid:instance_id>", methods=['GET'])
def get_event(instance_id):
    return get_memory_part(instance_id, 'event')


@bp.route("/entities/<uuid:instance_id>", methods=['GET'])
def get_entities(instance_id):
    return get_grouped(instance_id, 'entities')


@bp.route("/maps/<uuid:instance_id>", methods=['GET'])
def get_maps(instance_id):
    return get_grouped(instance_id, 'maps')


def get_memory_part(instance_id, collection):
    header_query = {"header.instanceId": str(instance_id)}

    db = get_database()
    data = db[collection].find_one(header_query)
    if data:
        data.pop('_id')
        return jsonify(data)


def get_grouped(instance_id, collection):
    header_query = {"header.instanceId": str(instance_id)}

    db = get_database()
    items = [item for item in db[collection].find(header_query)]
    ret = dict()
    for item in items:
        if not item['type'] in ret.keys():
            ret[item['type']] = []
        ret[item['type']].append(item['data'])

    return jsonify(ret)
