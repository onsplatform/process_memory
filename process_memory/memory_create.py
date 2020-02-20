import util
from flask import current_app as app
from datetime import datetime
from flask_api import status
from flask import Blueprint, request, make_response
from bson.json_util import loads, CANONICAL_JSON_OPTIONS
from process_memory.db import get_database
from process_memory.memory_queries import find_head

bp = Blueprint('memory', __name__)


@bp.route("/<uuid:instance_id>", methods=['POST'])
@bp.route("/<uuid:instance_id>/commit", methods=['POST'])
@bp.route("/<uuid:instance_id>/create", methods=['POST'])
def create_memory(instance_id):
    if request.data:
        app.logger.debug('creating process memory: ' + str(instance_id))
        json_data = loads(request.data, json_options=CANONICAL_JSON_OPTIONS)
        app.logger.debug(json_data)
        entities, event, fork, maps, header = _get_memory_body(json_data)
        _create_or_update_memory(entities, event, fork, maps, header)
        return make_response('', status.HTTP_201_CREATED)


@bp.route("/clone/<uuid:from_instance_id>/<uuid:to_instance_id>", methods=['POST'])
def clone_memory(from_instance_id, to_instance_id):
    response = find_head(from_instance_id)
    if response:
        json_data = loads(response.data)
        json_data['reproduction'] = {
            'from': str(from_instance_id),
            'to': str(to_instance_id)
        }
        json_data['instanceId'] = str(to_instance_id)
        entities, event, fork, maps, header = _get_memory_body(json_data)
        _create_or_update_memory(entities, event, fork, maps, header)
        return make_response('', status.HTTP_201_CREATED)


def _create_or_update_memory(entities, event, fork, maps, header):
    db = get_database()
    _persist_event(db, event, header) if event else None
    _persist_fork(db, fork, header) if fork else None
    _delete_maps(db, header) if maps else None
    _delete_entities(db, header) if entities else None
    _persist_maps(db, maps, header) if maps else None
    _persist_entities(db, entities, header) if entities else None


def _get_memory_body(json_data):
    json_data = json_data.pop('json', json_data)
    event = json_data.pop('event', None)
    fork = json_data.pop('fork', None)
    maps = json_data.pop('map', {}).pop('content', None)
    entities = json_data.pop('dataset', {}).pop('entities', None)
    json_data['timestamp'] = event.get('timestamp', datetime.utcnow())
    header = _create_header_object(event)
    return entities, event, fork, maps, header


def _persist_event(db, event, header):
    new_event = dict()
    new_event['header'] = header
    new_event['name'] = event.get('name', None)
    new_event['scope'] = event.get('scope', None)
    new_event['instanceId'] = event.get('instanceId', None)
    new_event['reproduction'] = header['reproduction']
    new_event['timestamp'] = util.get_datetime_from(event.get('timestamp'))
    new_event['owner'] = event.get('owner', None)
    new_event['tag'] = event.get('tag', None)
    new_event['branch'] = event.get('branch', None)
    new_event['payload'] = event.get('payload', None)
    query = {"header.instanceId": str(header['instanceId'])}
    db['event'].update_one(query, {'$set': new_event}, upsert=True)


def _persist_fork(db, fork, header):
    new_fork = dict()
    for key, value in fork.items():
        if value:
            new_fork[key] = value
    new_fork['header'] = header
    query = {"header.instanceId": str(header['instanceId'])}
    db['fork'].update_one(query, {'$set': new_fork}, upsert=True)


def _delete_entities(db, header):
    query = {"header.instanceId": str(header['instanceId'])}
    db['entities'].delete_many(query)


def _delete_maps(db, header):
    query = {"header.instanceId": str(header['instanceId'])}
    db['maps'].delete_many(query)


def _persist_maps(db, maps, header):
    docs = list()
    for key in maps.keys():
        docs.append({'header': header, 'data': maps[key], 'type': key})
    db['maps'].insert_many(docs)


def _persist_entities(db, entities, header):
    docs = list()
    for key in entities.keys():
        if entities[key]:
            for value in entities[key]:
                docs.append({'header': header, 'data': value, 'type': key})
    db['entities'].insert_many(docs)


def _create_header_object(json_data):
    new_header = dict()
    new_header['instanceId'] = json_data.get('instanceId')
    new_header['processId'] = json_data.get('processId')
    new_header['systemId'] = json_data.get('systemId')
    new_header['eventOut'] = json_data.get('eventOut', None)
    new_header['commit'] = json_data.get('commit', None)
    new_header['reproduction'] = json_data.get('reproduction', None)
    new_header['timestamp'] = util.get_datetime_from(json_data.get('timestamp', None))
    return new_header
