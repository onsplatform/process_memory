from flask import Blueprint, request, jsonify, make_response
from flask_api import status
from process_memory.db import get_db_collection
from pymongo import ASCENDING
import util

bp = Blueprint('collection', __name__)


@bp.route("/<uuid:collection>", methods=['POST'])
def post_collection(collection: str):
    """
    Collection is the same as instance_id, a bucket of documents inside MongoDB, not another database.
    :param collection: Collection unique id identifier.
    :return: HTTP_STATUS
    """
    db = get_db_collection()
    app_collection = db.get_collection(str(collection))

    document = util.create_document(request.get_json())
    # persist document
    post_id = app_collection.insert_one(document).inserted_id
    app_collection.create_index([("timestamp", ASCENDING)])

    return make_response(jsonify(document_id=str(post_id), instance_id=collection), status.HTTP_201_CREATED)


@bp.route("/<uuid:collection>", methods=['GET'])
def get_collection(collection: str):
    """
    Find content inside a collection. Requests parameters as a dictionary:
    {
    "tipo_de_usina": "termica",
    "usina": "Angra"
    }
    :param collection: Collection unique id identifier.
    :return: List of documents or nothing
    """
    if request.data:
        db = get_db_collection()
        app_collection = db.get_collection(str(collection)).find(request.get_json())

        if app_collection.count() > 0:
            response = [item for item in app_collection]
            return make_response(jsonify(response), status.HTTP_200_OK)

    return make_response("", status.HTTP_204_NO_CONTENT)


@bp.route("/<uuid:collection>", methods=['PUT'])
def replace_collection(collection):
    """
    Replaces a single document inside the collection with another document.
    Filter is what is going to be found. It should be a dictionary with a single or various keys and values.
    Replacement is the new document that is going to replace the older one found.
    Sample:
    {
        "filter": {"tipoUsina": "termica", "nomeUsina": "Angra"},
        "replacement": { "tipoUsina":"hidro", "nomeUsina":"Tucurui" }
    }
    Parameters above will search for all documents in the collection, return one, replace it with the new document.
    :param collection: collection: Collection unique id identifier.
    :return: Dictionary with either the old document or empty.
    """
    if request.data:
        db = get_db_collection()
        app_collection = db.get_collection(str(collection))

        finder = request.get_json().get('filter')
        document = request.get_json().get('replacement')

        response: dict = app_collection.find_one_and_replace(filter=finder, replacement=document)

        if response:
            return make_response(jsonify(response), status.HTTP_200_OK)

    return make_response("", status.HTTP_304_NOT_MODIFIED)