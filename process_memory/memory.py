from flask import Blueprint, request, make_response
from flask_api import status
from process_memory.db import get_database, get_grid_fs
import sys
import util
from pymongo import DESCENDING
from bson.json_util import dumps, loads, CANONICAL_JSON_OPTIONS
from process_memory.dataset import *


bp = Blueprint('memory', __name__)

MAX_BYTES: int = 16000000
DATA_SIZE: int = None
LARGE_COLLECTIONS = ('usina', 'unidadegeradora', 'potenciauge', 'franquiauge', 'eventomudancaestadooperativo')


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

        _persist(json_data)

        # Everything OK! Confirm all collections are saved.
        return make_response('Success', status.HTTP_201_CREATED)

    return make_response("There is no data in the request.", status.HTTP_417_EXPECTATION_FAILED)


def _persist(json_data):
    # Extract the payload into memories. Create a header to link them all.
    event: dict = {'event': json_data.pop('event', None)}
    map: dict = {'map': json_data.pop('map', None)}
    fork: dict = {'fork': json_data.pop('fork', None)}
    dataset: dict = json_data.pop('dataset', None)
    header: dict = _create_header(json_data)

    # save event
    # save map
    # save fork

    # TODO: Refactor this
    # Instantiate a new DataSet Schema
    _persist_dataset(dataset, header)


def _persist_dataset(dataset: dict, header: dict):

    new_entity = Entities()
    new_dataset = Dataset()
    db = get_database()
    for key, value in dataset.get('entities').items():
        if value:
            if key not in LARGE_COLLECTIONS:
                new_entity[key] = value
            else:
                new_entity[key] = db[key].insert_many([{'header': header, 'data': item} for item in value]) \
                    .inserted_ids

    # Create a Dataset and populate it
    new_dataset.header = header
    new_dataset.entities = new_entity
    new_dataset.save()


def _create_header(header):
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


@bp.route("/memory/<uuid:instance_id>")
@bp.route("/memory/<uuid:instance_id>/head")
def find_head(instance_id):
    """
    Finds and returns the entire data collection for that particular instance id.
    :param instance_id: UUID with the desired instance id.
    :return:
    """
    head_query = {"header.instanceId": str(instance_id)}
    db = get_database()
    event_memory = db['events'].find(head_query).sort('timestamp', DESCENDING)
    map_memory = db['maps'].find(head_query).sort('timestamp', DESCENDING)
    dataset_memory = db['dataset'].find(head_query).sort('timestamp', DESCENDING)
    fork_memory = db['fork'].find(head_query).sort('timestamp', DESCENDING)

    data = event_memory, map_memory, dataset_memory, fork_memory
    result = dumps(data)

    return make_response(result, status.HTTP_200_OK)


def _memory_insert(collection: str, data: dict):
    """
    Inserts a new document object into the database
    :param collection: The collection that the document belongs and should be saved to.
    :param data: The data (dictionary) to save.
    :return: Document Object ID.
    """
    try:
        if sys.getsizeof(data) > MAX_BYTES:
            raise ValueError("Document is too large. Use memory_file_insert if object is above " + str(MAX_BYTES))
        db = get_database()
        result = db[collection].insert_one(data)
        return result.inserted_id
    except ValueError as ve:
        print(ve)


def _memory_file_insert(instance_uuid: str, header: dict, data: bytes, collection: str):
    """
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
