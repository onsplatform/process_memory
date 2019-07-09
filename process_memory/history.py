from flask import Flask, Blueprint, g, request, jsonify, make_response
from flask_api import status
import util
from pymongo import ASCENDING

from process_memory.db import get_db_collection

bp = Blueprint('history', __name__)


@bp.route("/<uuid:instance_id>/history")
def get_history(instance_id):
	"""
	Lists the last 100 documents from the history, from most recent to oldest.
	"""
	first = request.args.get('first', default=-1, type=int)
	last = request.args.get('last', default=-1, type=int)

	return make_response(str(first) + "___" + str(last), status.HTTP_200_OK)


@bp.route("/<uuid:instance_id>/history/first/<int:number_of_documents>")
def get_history_since(instance_id, number_of_documents):
	"""
	Lists the first n documents, from oldest to newest.
	"""
	app_db = get_db_collection()
	app_collection = app_db.get_collection(str(instance_id))
	history_documents = app_collection.find().sort('timestamp', ASCENDING).limit(number_of_documents)
	return make_response(util.create_document(history_documents), status.HTTP_200_OK)


@bp.route("/<uuid:instance_id>/history/last/<int:limit>")
def get_history_until(instance_id, limit):
	"""
	Lists the last n documents, from most recent to the oldest. There is a hard limit of 1000 (one thousand) documents.
	TODO: test if we should do this or just use the current contract.
	"""
	return status.HTTP_204_NO_CONTENT