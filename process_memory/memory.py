import util

from datetime import datetime

from flask_api import status
from flask import Blueprint, request, make_response

from bson.json_util import loads, CANONICAL_JSON_OPTIONS

from process_memory.models.event import *
from process_memory.models.header import Header
from process_memory.models.mapper import Map
from process_memory.models.fork import Fork
from process_memory.db import *

bp = Blueprint('memory', __name__)

DATA_SIZE: int = None
INSTANCE_HEADER = None


@bp.route("/memory/<uuid:instance_id>", methods=['POST'])
def persist_memory(instance_id):
    """
    Creates a memory of the provided json file with the provided key.
    :param instance_id: UUID or GUID provided by the client app.
    :return: HTTP_STATUS
    """
    if request.data:
        json_data: dict = loads(request.data, json_options=CANONICAL_JSON_OPTIONS)
        assert (type(json_data) is dict), "Method expects a dictionary and received: " + str(type(json_data))

        # Extract the payload into memories. Create a header to link them all.
        event: dict = json_data.pop('event', None)
        mapper: dict = json_data.pop('map', None)
        fork: dict = json_data.pop('fork', None)
        dataset: dict = json_data.pop('dataset', None)
        json_data['timestamp'] = event.get('timestamp', datetime.datetime.utcnow())

        global INSTANCE_HEADER
        INSTANCE_HEADER = json_data

        # save data
        get_database()
        _persist_event(event) if event else None
        _persist_map(mapper['content'], 'maps') if mapper else None
        _persist_fork(fork) if fork else None
        _persist_dataset(dataset['entities'], 'entities') if dataset else None

        # Everything OK! Confirm all collections are saved.
        return make_response('Success', status.HTTP_201_CREATED)

    return make_response("There is no data in the request.", status.HTTP_417_EXPECTATION_FAILED)


def _persist_event(event: dict):
    new_event = Event()

    new_event.header = _create_header_object(INSTANCE_HEADER)
    new_event.name = event.get('name', None)
    new_event.scope = event.get('scope', None)
    new_event.instanceId = event.get('instanceId', None)
    new_event.timestamp = util.get_datetime_from(event.get('timestamp'))
    new_event.owner = event.get('owner', None)
    new_event.tag = event.get('tag', None)
    new_event.branch = event.get('branch', None)
    new_event.payload = event.get('payload', None)

    new_event.save()


def _persist_mapper(mapper: dict):
    new_map = Map()
    new_map.header = _create_header_object(INSTANCE_HEADER)
    for key, value in mapper.items():
        if value:
            new_map[key] = value

    return new_map.save()


def _persist_fork(fork: dict):
    new_fork = Fork()
    new_fork.header = _create_header_object(INSTANCE_HEADER)
    for key, value in fork.items():
        if value:
            new_fork[key] = value

    return new_fork.save()


def _persist_map(dataset, collection):
    docs = list()
    db = get_database()
    for key in dataset.keys():
        docs.append({'header': INSTANCE_HEADER, 'data': dataset[key], 'type': key})
    db[collection].insert_many(docs)


def _persist_dataset(dataset, collection):
    docs = list()
    db = get_database()
    for key in dataset.keys():
        if dataset[key]:
            for value in dataset[key]:
                docs.append({'header': INSTANCE_HEADER, 'data': value, 'type': key})
    db[collection].insert_many(docs)


def _create_header_object(header: dict):
    new_header = Header()
    new_header.instanceId = header.get('instanceId')
    new_header.processId = header.get('processId')
    new_header.systemId = header.get('systemId')
    new_header.eventOut = header.get('eventOut', None)
    new_header.commit = header.get('commit', None)
    new_header.timestamp = util.get_datetime_from(header.get('timestamp', None))
    return new_header
