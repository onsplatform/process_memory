from flask import Blueprint, request, make_response, current_app
from flask_api import status
from process_memory.db import get_database, get_grid_fs
import sys
import util
import json

bp = Blueprint('memory', __name__)

MAX_BYTES = 120000000

# TODO: read the latest document from memory
@bp.route("/memory/<uuid:instance_id>/head")
def find_head(instance_id):
    return instance_id


@bp.route("/memory/<uuid:instance_id>", methods=['POST'])
@bp.route("/memory/<uuid:instance_id>/commit", methods=['POST'])
def create_memory(instance_id):
    """
    Creates a memory of the provided json file with the provided key.
    :param instance_id: UUID or GUID provided by the client app.
    :return:
    """
    json_data: dict
    if request.data:
        json_data = request.get_json()
        # Extract the payload into memories. Create a header to link them all.
        event_memory: dict = json_data.pop('event')
        map_memory: dict = json_data.pop('map')
        dataset_memory: dict = json_data.pop('dataset')
        header: dict = json_data

        # If all data is smaller than 15 million bytes (most cases)
        if request.content_length < MAX_BYTES:
            # Include header in all memories. They will be linked by it.
            event_memory = util.include_header(header, event_memory)
            map_memory = util.include_header(header, map_memory)
            dataset_memory = util.include_header(header, dataset_memory)

            # Insert data
            _memory_insert('events', event_memory)
            _memory_insert('maps', map_memory)
            _memory_insert('dataset', dataset_memory)

            # Everything OK! Confirm all collections are saved.
            return make_response('Success', status.HTTP_201_CREATED)

        # Special treatment for large files.
        # Now, we check which parts are really large (above 15 million bytes) and save them to file.
        db = get_database()
        fs = get_grid_fs()
        if sys.getsizeof(event_memory) < MAX_BYTES:
            db['events'].insert_one(event_memory)

        if sys.getsizeof(map_memory) < MAX_BYTES:
            db['maps'].insert_one(map_memory)

        # sys.getsizeof(map_memory)
        # sys.getsizeof(dataset_memory)
        mydata = request.data
        new_memory = bytes(json.dumps(event_memory), 'utf-8')

        event_memory = util.include_header(header, util.compress(json.dumps(event_memory)))
        fs = get_grid_fs()

    if request.data and request.content_length > MAX_BYTES:
        # Compress the data > Connect to GridFS > Save File with instance_id name > Get unique file Id.
        compressed_data = util.compress(request.data)
        fs = get_grid_fs()
        file_id = fs.put(compressed_data, filename=str(instance_id)+".snappy", metadata=_create_header())

    return make_response("From (bytes): " + str(doc_size) + " To (bytes): " + str(sys.getsizeof(compressed_data)) +
                         "\nNew file id: " + str(file_id), status.HTTP_200_OK)


def _memory_insert(collection: str, data: dict):
    db = get_database()
    result = db[collection].insert_one(data)
    return result.inserted_id


def _create_header():
    header = {
        "processId": "4c7735de-6992-4c1a-ab73-e4114b2da42a",
        "systemId": "a22d9e4d-c352-4ac2-8321-2c496fe3a116",
        "instanceId": "c1996da1-ae96-4e99-9b80-bec749d2d67c",
        "eventOut": "confirmar.estruturacao.cenario.request.done",
        "commit": True
    }

    return header

"""
TODO: insert a document into memory

TODO: use GRIDFS if post size is larger than 10 MB. Compact json file before saving.
TODO: will need 3 create functions: create_map, create_event, create_dataset
TODO: will need 3 get functions: get_map, get_event, get_dataset¹
TODO: ¹get_dataset will have to deal with gzip compression and decompression for the >400MB sets.
"""