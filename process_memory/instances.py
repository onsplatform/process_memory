from flask import Blueprint, request, jsonify, make_response
from flask_api import status
from bson.json_util import dumps
import util
from process_memory.db import get_database_name
from pymongo import ASCENDING, DESCENDING


bp = Blueprint('instances', __name__)


@bp.route("/instances")
def list_instances():
    """
    Lists all the ids of the instances in the database.
    :return: list of json documents that contains the instances in the database collection.
    """
    db = get_database_name()
    collection_list = db.list_collection_names()

    return make_response(dumps(collection_list), status.HTTP_200_OK)


# The 2 top routes are compatibility only. They should, by all means, be avoided.
@bp.route("/<uuid:instance_id>/create", methods=['POST'])
@bp.route("/<uuid:instance_id>/commit", methods=['POST'])
@bp.route("/instances/<uuid:instance_id>", methods=['GET', 'POST'])
def instance(instance_id):
    """
    Creates a collection and inserts a document to host the app instance.
    :param instance_id: The unique identifier of the instance.
    :return: list of instances, including the new ones.
    """
    db = get_database_name()
    app_collection = db.get_collection(str(instance_id))
    size = request.content_length
    import pdb; pdb.set_trace()
    print(size)
    print(request.max_content_length)
    if request.method == 'POST' and request.data:
        document = util.create_document(request.get_json())
        # persist document
        post_id = app_collection.insert_one(document).inserted_id
        app_collection.create_index([("timestamp", ASCENDING)])

        return make_response(jsonify(document_id=str(post_id), instance_id=instance_id), status.HTTP_201_CREATED)

    app_collection = db.get_collection(str(instance_id))
    col_info_response = {
        "full_name": app_collection.full_name,
        "aprox_doc_count": app_collection.estimated_document_count(maxTimeMS=5000)
    }

    return make_response(jsonify(col_info_response), status.HTTP_200_OK)


@bp.route("/<uuid:instance_id>/head")
def find_head(instance_id):
    """
    Gets the latest document of the instance collection
    :param instance_id: unique instance identification
    :return: the latest (most recent) document in the given instance.
    """
    db = get_database_name()
    app_collection = db.get_collection(str(instance_id))
    latest_document = app_collection.find().sort('timestamp', DESCENDING).limit(1)

    return make_response(dumps(latest_document), status.HTTP_200_OK)


@bp.route("/<uuid:instance_id>/first")
def find_first(instance_id):
    """
    Gets the first document of the instance collection.
    :param instance_id: unique instance identification
    :return:
    """
    db = get_database_name()
    app_collection = db.get_collection(str(instance_id))
    first_document = app_collection.find().sort('timestamp', direction=ASCENDING).limit(1)

    return make_response(dumps(first_document), status.HTTP_200_OK)


@bp.route("/<uuid:instance_id>/first/<int:number_of_documents>")
def get_first_documents(instance_id, number_of_documents):
    """
    Lists the first n documents, from oldest to newest.
    :param instance_id: unique instance identification
    :param number_of_documents:
    :return:
    """
    db = get_database_name()
    # This is done to protect the database against large requests for no reason.
    if number_of_documents > 1000:
        number_of_documents = 1000

    app_collection = db.get_collection(str(instance_id))
    history_documents = app_collection.find().sort('timestamp', ASCENDING).limit(number_of_documents).limit(1)

    return make_response(dumps(history_documents), status.HTTP_200_OK)


# The top route is legacy support. Should be avoided in the future.
@bp.route("/<uuid:from_instance_id>/<uuid:to_instance_id>/clone", methods=['POST'])
@bp.route("/reproduction/<uuid:from_instance_id>/<uuid:to_instance_id>", methods=['POST'])
def clone_instance(from_instance_id, to_instance_id):
    """
    Lists the first n documents, from oldest to newest.
    :param from_instance_id: unique collection identification to copy from
    :param to_instance_id: unique collection identification destination
    return: id of the new document inside the collection
    """
    db = get_database_name()
    source_collection = db.get_collection(str(from_instance_id))
    projection_fields = {'_id': False}

    # Find the first document of the "from_instance_id" collection. Projection does not bring old id.
    source_document = source_collection.find(projection=projection_fields).sort('timestamp', ASCENDING).limit(1)
    # Prepare a new collection, with the destination UUID.
    # Save the document. New document id will be assigned by database.
    destination_collection = db.get_collection(str(to_instance_id))
    destination_document = destination_collection.insert_one(source_document[0])

    return make_response(str(destination_document.inserted_id), status.HTTP_201_CREATED)