from flask import Flask, Blueprint, g, request, jsonify, make_response
from flask_api import status
import util

from process_memory.db import get_db_collection

bp = Blueprint('history', __name__)

@bp.route("/<uuid:instance_id>/history")
def getHistory(instance_id):
	'''
	Lists the last 1000 documents from the history, from most recent to oldest.
	'''
	first = request.args.get('first', default=-1, type = int)
	last = request.args.get('last', default=-1, type = int)
    
	return make_response(str(first) + "___" + str(last),status.HTTP_200_OK)