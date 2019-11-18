from flask import Blueprint, request, make_response, current_app
from flask_api import status
from process_memory.db import get_database, get_grid_fs
import sys
import util


bp = Blueprint('memory', __name__)

MAX_BYTES = 1200

# TODO: read the latest document from memory
@bp.route("/memory/<uuid:instance_id>", methods=['POST'])
@bp.route("/memory/<uuid:instance_id>/commit", methods=['POST'])
def create_memory(instance_id):
    """
    Creates a memory of the provided json file with the provided key.
    :param instance_id: UUID or GUID provided by the client app.
    :return: HTTP_STATUS
    """
    json_data: dict
    large_request: bool = False
    if request.content_length > MAX_BYTES:
        large_request = True
    if request.data:
        json_data = request.get_json()
        # Extract the payload into memories. Create a header to link them all.
        event_memory: dict = json_data.pop('event')
        map_memory: dict = json_data.pop('map')
        dataset_memory: dict = json_data.pop('dataset')
        header: dict = json_data

        # if request.content_length > MAX_BYTES:
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

    # Todo: Special treatment for large files.
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


def _memory_file_insert(instance_id: str, header: dict, data: bytes):
    """
    Inserts a new document as a compressed file into the database. Header will be saved as metadata.
    :param data: The data (bytes) to be compressed and inserted.
    :param instance_id: The instance_id to which this record belongs to.
    :param header: Header is data to identify the file. It will be saved as metadata.
    :return: Tuple with (File Object ID, File name).
    """
    assert (type(data) is bytes), "For file compression and saving, data should be bytes."
    compressed_data = util.compress(data)
    file_name = instance_id + ".snappy"
    fs = get_grid_fs()
    file_id = fs.put(compressed_data, filename=file_name, metadata=header)
    return file_id, file_name


def _memory_save(instance_uuid: str, collection: str, memory_header: dict, data: dict):
    """
    Function to save the data into memory.
    :param instance_uuid:
    :param collection:
    :param memory_header:
    :param data:
    :return:
    """
    if sys.getsizeof(data) > MAX_BYTES:
        data_bytes = util.convert_to_bytes(data)
        # Insert a file with header information inside the metadata field. Update header with the file info.
        file_id, file_name = _memory_file_insert(data_bytes, instance_id=instance_uuid, header=memory_header)
        memory_header.update({"file_id": file_id, "file_name": file_name})
        # Insert a record into the correct collection, with a reference to a file with the large payload.
        return _memory_insert(collection, memory_header)

    return _memory_insert(collection, data)
