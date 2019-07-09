from flask import Blueprint, request, jsonify, make_response
from flask_api import status
from process_memory.db import get_db_collection
from pymongo import ASCENDING, DESCENDING
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
    db = get_db_collection()
    app_collection = db.get_collection(str(collection))

    response = app_collection.find()

    return NotImplemented


@bp.route("/<uuid:collection>", methods=['PUT'])
def update_collection():
    return NotImplemented


"""
server.post('/:collection', (req, res, next) => {

    var collection_name = req.params.collection;
    data = {}
    if (req.body) {
        data = req.body;
    }
    sto.saveDocument(collection_name, data).
        then((result) => {
            res.send(200, result);
        }).
        catch((err) => {
            console.log("Erro no 'create':", err);
            res.send(500, err.toString());
        });
});


server.get('/:collection', (req, res, next) => {
    var collection_name = req.params.collection;
    var query = ConvertJsonStringToObject(req.query);
    delete query["app_origin"]

    sto.findDocument(collection_name, query || {}).
        then((result) => {
            res.send(result);
        }).
        catch((err) => {
            console.log("Erro no 'first':", err);
            res.send(500, err.toString());
        });
});

server.put('/:collection', (req, res, next) => {
    var collection_name = req.params.collection;
    data = {}
    if (req.body) {
        data = req.body;
    }
    var query = ConvertJsonStringToObject(req.query);
    delete query["app_origin"]
    sto.updateDocument(collection_name, query || {}, data).
        then((result) => {
            res.send(result);
        }).
        catch((err) => {
            console.log("Erro no 'first':", err);
            res.send(500, err.toString());
        });
});

"""