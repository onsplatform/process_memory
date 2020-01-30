import util
from datetime import datetime
from flask_api import status
from flask import Blueprint, request, make_response
from bson.json_util import loads, CANONICAL_JSON_OPTIONS
from process_memory.db import get_database

bp = Blueprint('memory', __name__)


@bp.route("/memory/<uuid:instance_id>", methods=['POST'])
@bp.route("/memory/<uuid:instance_id>/commit", methods=['POST'])
def create_memory(instance_id):
    if request.data:
        json_data = loads(request.data, json_options=CANONICAL_JSON_OPTIONS)
        entities, event, fork, maps, header = _get_memory_body(json_data)
        _create_or_update_memory(entities, event, fork, maps, header)
        return make_response('Success', status.HTTP_201_CREATED)


@bp.route("/memory/clone/<uuid:from_instance_id>/<uuid:to_instance_id>", methods=['POST'])
def clone_memory(instance_id):
    if request.data:
        json_data = loads(request.data, json_options=CANONICAL_JSON_OPTIONS)
        entities, event, fork, maps, header = _get_memory_body(json_data)

def _create_or_update_memory(entities, event, fork, maps, header):
    db = get_database()
    _persist_event(db, event, header) if event else None
    _persist_fork(db, fork, header) if fork else None
    _delete_maps(db, header) if maps else None
    _delete_entities(db, header) if entities else None
    _persist_maps(db, maps, header) if maps else None
    _persist_entities(db, entities, header) if entities else None


def _get_memory_body(json_data):
    event = json_data.pop('event', None)
    fork = json_data.pop('fork', None)
    maps = json_data.pop('map', None).pop('content', None)
    entities = json_data.pop('dataset', None).pop('entities', None)
    json_data['timestamp'] = event.get('timestamp', datetime.datetime.utcnow())
    header = _create_header_object(json_data)
    return entities, event, fork, maps, header


def _persist_event(db, event, header):
    new_event = dict()
    new_event['header'] = header
    new_event['name'] = event.get('name', None)
    new_event['scope'] = event.get('scope', None)
    new_event['instanceId'] = event.get('instanceId', None)
    new_event['timestamp'] = util.get_datetime_from(event.get('timestamp'))
    new_event['owner'] = event.get('owner', None)
    new_event['tag'] = event.get('tag', None)
    new_event['branch'] = event.get('branch', None)
    new_event['payload'] = event.get('payload', None)
    query = {"header.instanceId": str(header['instanceId'])}
    db['event'].update_one(query, {'$set': new_event}, upsert=True)


def _persist_fork(db, fork, header):
    new_fork = dict()
    new_fork['header'] = header
    for key, value in fork.items():
        if value:
            new_fork[key] = value
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


def _create_header_object(header):
    new_header = dict()
    new_header['instanceId'] = header.get('instanceId')
    new_header['processId'] = header.get('processId')
    new_header['systemId'] = header.get('systemId')
    new_header['eventOut'] = header.get('eventOut', None)
    new_header['commit'] = header.get('commit', None)
    new_header['timestamp'] = util.get_datetime_from(header.get('timestamp', None))
    return new_header
