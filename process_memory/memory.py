from flask import Blueprint, request, jsonify, make_response
from flask_api import status
from bson.json_util import dumps
import util
from process_memory.db import get_database
from pymongo import ASCENDING, DESCENDING


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
    # Get the document size.
    doc_size = request.content_length
    # TODO: check if the size is above 10 million bytes.
    if request.data and request.content_length > 10000000:
        doc_size = 10000000

    db = get_database()
    app_collection = db.get_collection(str(instance_id))

    if request.method == 'POST' and request.data:
        document = util.create_document(request.get_json())
        # persist document
        post_id = app_collection.insert_one(document).inserted_id
        app_collection.create_index([("timestamp", ASCENDING)])

    return make_response(str(doc_size), status.HTTP_200_OK)

"""
TODO: insert a document into memory

TODO: use GRIDFS if post size is larger than 10 MB. Compact json file before saving.
TODO: will need 3 create functions: create_map, create_event, create_dataset
TODO: will need 3 get functions: get_map, get_event, get_dataset¹
TODO: ¹get_dataset will have to deal with gzip compression and decompression for the >400MB sets.
"""