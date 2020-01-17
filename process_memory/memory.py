from flask import Blueprint, request, make_response
from flask_api import status
import sys
import util
from pymongo import DESCENDING
from bson.json_util import dumps, loads, CANONICAL_JSON_OPTIONS
from process_memory.models.dataset import *
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

        global INSTANCE_HEADER
        INSTANCE_HEADER = json_data

        # save data
        _persist_event(event) if event else None
        _persist_mapper(mapper) if mapper else None
        _persist_fork(fork) if fork else None
        _persist_dataset(dataset) if dataset else None

        # Everything OK! Confirm all collections are saved.
        return make_response('Success', status.HTTP_201_CREATED)

    return make_response("There is no data in the request.", status.HTTP_417_EXPECTATION_FAILED)


def _persist_event(event: dict):

    # Payloads may be very large, with thousands of events. This must be treated with care.
    new_payload = Payload()
    new_ocorrencia = RegistrosOcorrencia()
    new_registro = Registros()
    new_event = Event()

    # Create Event Payload
    new_ocorrencia.registros = _create_payload(event, new_payload, new_registro)
    new_payload.registrosocorrencia = new_ocorrencia

    new_event.header = _create_header_object(INSTANCE_HEADER)
    new_event.name = event.get('name', None)
    new_event.scope = event.get('scope', None)
    new_event.instanceId = event.get('instanceId', None)
    new_event.timestamp = event.get('timestamp', None)
    new_event.owner = event.get('owner', None)
    new_event.tag = event.get('tag', None)
    new_event.branch = event.get('branch', None)
    new_event.payload = new_payload

    new_event.save()
    return None


def _persist_mapper(mapper: dict):
    """
    Persist Map Memory Object
    :param mapper: Map data
    :return: saved map object
    """
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


def _persist_dataset(dataset: dict):
    """
    Persist a new dataset and its dependencies.
    :param dataset:
    :return:
    """
    large_dataset = ('unidadegeradora', 'potenciauge', 'franquiauge', 'eventomudancaestadooperativo')

    new_entity = Entities()
    _bulk_insert(dataset, new_entity, 'entities', large_dataset)

    # Create a new Dataset and populate it
    new_dataset = Dataset()
    new_dataset.header = _create_header_object(INSTANCE_HEADER)
    new_dataset.entities = new_entity
    new_dataset.save()


def _create_payload(event, new_payload, new_registro):
    """
    This may be better written if the payload is simplified. _bulk_insert could be used.
    :param event: event collection
    :param new_payload: This is the event payload that must be broken apart.
    :param new_registro:
    :return: A collection of registros ids
    """
    db = get_database()
    for key, value in event.get('payload').items():
        if value:
            if key not in ('Eventos', 'RegistrosOcorrencia'):
                new_payload[key] = value
            elif key == 'Eventos':
                new_payload[key] = db[key].insert_many(
                    [{'header': INSTANCE_HEADER, 'data': item} for item in value]).inserted_ids
            elif key == 'RegistrosOcorrencia':
                new_registro = db['registros'].insert_many(
                    [{'header': INSTANCE_HEADER, 'data': item} for item in value.get('Registros')]).inserted_ids
    return new_registro


def _bulk_insert(from_collection: dict, to_collection: dict, payload: str, large_data: tuple):
    """
    Insert multiple data into the destination collection. Uses PyMongo´s insert_many.
    :param from_collection: The collection from which data should be extracted.
    :param to_collection: The destination collection, that means, the collection that should receive multiple data.
    :param payload: List name
    :param large_data: A tuple with information that should be bulk_inserted.
    :return:
    """
    db = get_database()
    for key, value in from_collection.get(payload).items():
        if value:
            if key not in large_data:
                to_collection[key] = value
            else:
                to_collection[key] = db[key].insert_many(
                    [{'header': INSTANCE_HEADER, 'data': item} for item in value]).inserted_ids


def _create_header_object(header: dict):
    """
    Create an instance of Header(DynamicEmbeddedDocument) to be embedded in another class.
    :param header: Dictionary containing the data that should be used as composite primary key for documents.
    :return: instance of Dataset.Header(DynamicEmbeddedDocument)
    """
    new_header = Header()
    new_header.instanceId = header.get('instanceId')
    new_header.processId = header.get('processId')
    new_header.systemId = header.get('systemId')
    new_header.eventOut = header.get('eventOut', None)
    new_header.commit = header.get('commit', None)
    return new_header


@bp.route("/memory/<uuid:instance_id>/commit", methods=['POST'])
def create_memory(instance_id):
    """
    Creates a memory of the provided json file with the provided key.
    :param instance_id: UUID or GUID provided by the client app.
    :return: HTTP_STATUS
    """
    if request.data:
        global DATA_SIZE
        DATA_SIZE = request.content_length
        json_data: dict = loads(request.data)
        assert (type(json_data) is dict), "Method expects a dictionary and received: " + str(type(json_data))

        # Extract the payload into memories. Create a header to link them all.
        event_memory: dict = {'event': json_data.pop('event', None)}
        map_memory: dict = {'map': json_data.pop('map', None)}
        dataset: dict = json_data.pop('dataset', None)
        fork_memory: dict = {'fork': json_data.pop('fork', None)}
        header: dict = json_data

        # Include header in all memories. They will be linked by it.
        # Insert data
        header_id = _memory_save(collection='headers', header_id=None, data=header)
        _memory_save(collection='events', header_id=header_id, data=event_memory)
        _memory_save(collection='maps', header_id=header_id, data=map_memory)
        _memory_save(collection='dataset', header_id=header_id, data=dataset)
        _memory_save(collection='fork', header_id=header_id, data=fork_memory)

        # Everything OK! Confirm all collections are saved.
        return make_response('Success', status.HTTP_201_CREATED)

    return make_response("There is no data in the request.", status.HTTP_417_EXPECTATION_FAILED)


@bp.route("/memory/<uuid:instance_id>/head")
def find_head(instance_id):
    """
    Finds and returns the entire data collection for that particular instance id.
    :param instance_id: UUID with the desired instance id.
    :return:
    """
    header_query = {"header.instanceId": str(instance_id)}
    db = get_database()
    event_memory = db['event'].find(header_query).sort('timestamp', DESCENDING)
    map_memory = db['map'].find(header_query).sort('timestamp', DESCENDING)
    dataset_memory = db['dataset'].find(header_query).sort('timestamp', DESCENDING)
    fork_memory = db['fork'].find(header_query).sort('timestamp', DESCENDING)

    data = event_memory, map_memory, dataset_memory, fork_memory
    result = dumps(data)

    return make_response(result, status.HTTP_200_OK)


def _memory_insert(collection: str, data: dict):
    """
    !DEPRECATED!
    Inserts a new document object into the database
    :param collection: The collection that the document belongs and should be saved to.
    :param data: The data (dictionary) to save.
    :return: Document Object ID.
    """
    max_bytes = 16000000

    try:
        if sys.getsizeof(data) > max_bytes:
            raise ValueError("Document is too large. Use memory_file_insert if object is above " + str(max_bytes))
        db = get_database()
        result = db[collection].insert_one(data)
        return result.inserted_id
    except ValueError as ve:
        print(ve)


def _memory_file_insert(instance_uuid: str, header: dict, data: bytes, collection: str):
    """
    !DEPRECATED!
    Inserts a new document as a compressed file into the database. Header will be saved as metadata.
    :param data: The data (bytes) to be compressed and inserted.
    :param instance_uuid: The instance_id to which this record belongs to.
    :param header: Header is data to identify the file. It will be saved as metadata.
    :return: Tuple with (File Object ID, File name).
    """
    assert (type(data) is bytes), "For file compression and saving, data should be bytes."
    compressed_data = util.compress(data)
    fs = get_grid_fs()
    file_name = collection + "_" + str(instance_uuid) + ".snappy"
    file_id = fs.put(compressed_data, filename=file_name, metadata=header)
    return file_id


def _memory_save(collection: str, header_id: object, data: dict):
    """
    Save a process memory.
    :param collection: Collection (table) to save the data. Also used for filename.
    :param data: Payload to save, the usable data.
    :return: Object ID.
    """
    if header_id:
        data = util.include_header(header_id, data)

    return _memory_insert(collection, data)
