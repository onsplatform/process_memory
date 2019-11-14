from flask import Blueprint, request, make_response, current_app
from flask_api import status
from process_memory.db import get_database, get_grid_fs
import sys
import util
import json

bp = Blueprint('memory', __name__)

MAX_BYTES = 12000000

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


def _memory_file_insert(data: bytes, instance_id: str, header: dict):
    """
    Inserts a new document as a compressed file into the database.
    :param data: The data (bytes) to be compressed and inserted.
    :param instance_id: The instance_id to which this record belongs to.
    :param header: Header is data to identify the file. It will be saved as metadata.
    :return: Tuple with (File Object ID, File name).
    """
    assert (type(data) == bytes)
    compressed_data = util.compress(data)
    file_name = instance_id + ".snappy"
    fs = get_grid_fs()
    file_id = fs.put(compressed_data, filename=file_name, metadata=header)
    return file_id, file_name


def _memory_save(collection: str, data: dict):
    # 1. recebe uma coleção qualquer para inserir
    # 2. testa essa coleção para tamanho. Se for pequena, save comum.
    # 3. se for grande, obter o payload, comprimir ele, salvar o arquivo primeiro.
    # 4. junto com o salvamento do arquivo, salvar o header dentro do meta data do arquivo. Assim, o mesmo
    # pode ser encontrado tanto de forma direta pelo gridfs quanto pela coleção em que ele deveria pertencer.
    # 5. obter o id e o nome do arquivo, incluir no header e salvar eles como um documento comum.
    #
    db = get_database()
    result = db[collection].insert_one(data)
    return result.inserted_id
