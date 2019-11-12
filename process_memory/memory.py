from flask import Blueprint, request, make_response, current_app
from flask_api import status
from process_memory.db import get_database, get_grid_fs

from util import compress

bp = Blueprint('memory', __name__)


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
    doc_size = request.content_length
    # Check if there is a document and its size is above 12 million bytes.
    if request.data and request.content_length > 12000000:
        # Compress the data > Connect to GridFS > Save File with instance_id name > Get unique file Id.
        compressed_data = compress(request.data)
        fs = get_grid_fs()
        file_id = fs.put(compressed_data, filename=str(instance_id))
    """
    db = get_database()
    app_collection = db.get_collection(str(instance_id))

    if request.method == 'POST' and request.data:
        document = util.create_document(request.get_json())
        # persist document
        post_id = app_collection.insert_one(document).inserted_id
        app_collection.create_index([("timestamp", ASCENDING)])
    """
    return make_response("Original Data size: " + str(doc_size), status.HTTP_200_OK)


"""
TODO: insert a document into memory

TODO: use GRIDFS if post size is larger than 10 MB. Compact json file before saving.
TODO: will need 3 create functions: create_map, create_event, create_dataset
TODO: will need 3 get functions: get_map, get_event, get_dataset¹
TODO: ¹get_dataset will have to deal with gzip compression and decompression for the >400MB sets.
"""