from flask import Blueprint, request, jsonify, make_response
from flask_api import status
from bson.json_util import dumps
import util
from process_memory.db import get_database_name
from pymongo import ASCENDING, DESCENDING


bp = Blueprint('memory', __name__)

# TODO: read the latest document from memory
@bp.route("memory/<uuid:instance_id>/head")
def find_head(instance_id):
    return instance_id


@bp.route("memory/<uuid:instance_id>/", methods=['POST'])
def create_memory(instance_id):
    # TODO: insert a document into memory
    # TODO: check if the size is above 16 million bytes.
    # TODO: use GRIDFS if post size is larger than 16 MB.
    return instance_id