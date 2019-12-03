from flask import Blueprint, request, make_response, current_app
from flask_api import status
from process_memory.db import get_database, get_grid_fs
import sys
import util
from pymongo import ASCENDING, DESCENDING
from bson.json_util import dumps, loads, CANONICAL_JSON_OPTIONS

bp = Blueprint('memory', __name__)

MAX_BYTES: int = 16000000
DATA_SIZE: int = None


@bp.route("/memory/<uuid:instance_id>", methods=['POST'])
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
        json_data: dict = loads(request.data, json_options=CANONICAL_JSON_OPTIONS)

        # Extract the payload into memories. Create a header to link them all.
        event_memory: dict = {'event': json_data.pop('event', None)}
        map_memory: dict = {'map': json_data.pop('map', None)}
        dataset_memory: dict = {'dataset': json_data.pop('dataset', None)}
        fork_memory: dict = {'fork': json_data.pop('fork', None)}
        header: dict = json_data

        # Include header in all memories. They will be linked by it.
        # Insert data
        event_memory = util.include_header(header, event_memory)
        _memory_save(instance_id, collection='events', memory_header=header, data=event_memory)

        map_memory = util.include_header(header, map_memory)
        _memory_save(instance_id, collection='maps', memory_header=header, data=map_memory)

        dataset_memory = util.include_header(header, dataset_memory)
        _memory_save(instance_id, collection='dataset', memory_header=header, data=dataset_memory)

        fork_memory = util.include_header(header, fork_memory)
        _memory_save(instance_id, collection='fork', memory_header=header, data=fork_memory)

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
    head_query = {"header.instanceId": str(instance_id)}
    db = get_database()
    event_memory = db['events'].find(head_query).sort('timestamp', DESCENDING)
    map_memory = db['maps'].find(head_query).sort('timestamp', DESCENDING)
    dataset_memory = db['dataset'].find(head_query).sort('timestamp', DESCENDING)
    fork_memory = db['fork'].find(head_query).sort('timestamp', DESCENDING)

    result = event_memory, map_memory, dataset_memory, fork_memory

    return make_response(dumps(result, json_options=CANONICAL_JSON_OPTIONS), status.HTTP_200_OK)


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


def _memory_save(instance_uuid: str, collection: str, memory_header: dict, data: dict):
    """
    Save a process memory.
    :param instance_uuid: Unique ID, given by the application.
    :param collection: Collection (table) to save the data. Also used for filename.
    :param memory_header: Header data used to find all the artifacts.
    :param data: Payload to save, the usable data.
    :return: Object ID.
    """
    # check object size and proceed to compress and use gridfs
    if DATA_SIZE > MAX_BYTES:
        data_bytes = util.convert_to_bytes(data)
        # Insert a file with header information inside the metadata field. Update header with the file info.
        file_id = _memory_file_insert(instance_uuid, memory_header, data_bytes, collection)
        memory_header.update({"file_id": file_id})
        # Insert a record into the correct collection, with a reference to a file with the large payload.
        return _memory_insert(collection, memory_header)

    return _memory_insert(collection, data)
