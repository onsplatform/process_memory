from flask import Blueprint, request, make_response, current_app
from flask_api import status
from process_memory.db import get_database, get_grid_fs
import sys
import util

bp = Blueprint('memory', __name__)

MAX_BYTES: int = 16000000
DATA_SIZE: int = None

# TODO: read the latest document from memory
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
        json_data: dict = request.get_json()
        # Extract the payload into memories. Create a header to link them all.
        event_memory: dict = json_data.pop('event')
        map_memory: dict = json_data.pop('map')
        dataset_memory: dict = json_data.pop('dataset')
        header: dict = json_data

        # Include header in all memories. They will be linked by it.
        event_memory = util.include_header(header, event_memory)
        map_memory = util.include_header(header, map_memory)
        dataset_memory = util.include_header(header, dataset_memory)

        # Insert data
        _memory_save(instance_id, collection='events', memory_header=header, data=event_memory)
        _memory_save(instance_id, collection='maps', memory_header=header, data=map_memory)
        _memory_save(instance_id, collection='dataset', memory_header=header, data=dataset_memory)

        # Everything OK! Confirm all collections are saved.
        return make_response('Success', status.HTTP_201_CREATED)

    return make_response("There is no data in the request.", status.HTTP_417_EXPECTATION_FAILED)


@bp.route("/memory/<uuid:instance_id>/head")
def find_head(instance_id):
    return instance_id


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
    # check object size
    if DATA_SIZE > MAX_BYTES:
        data_bytes = util.convert_to_bytes(data)
        # Insert a file with header information inside the metadata field. Update header with the file info.
        file_id = _memory_file_insert(instance_uuid, memory_header, data_bytes, collection)
        memory_header.update({"file_id": file_id})
        # Insert a record into the correct collection, with a reference to a file with the large payload.
        return _memory_insert(collection, memory_header)

    return _memory_insert(collection, data)
