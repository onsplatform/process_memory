from flask import Flask, request, jsonify, make_response
from flask_api import status
import pymongo
import util
import process_memory

# app = Flask(__name__)
app = process_memory.create_app()
# client = pymongo.MongoClient("mongodb+srv://dbadmin:T4FbKpQoURhrilE7@docdb-jmi5t.mongodb.net")
# appDb = client.get_database("process_memory")
# appDb = process_memory.db.get_db()

"""
this is deprecated. using blueprints instead.
@app.route("/instances/<uuid:instance_id>", methods=['GET', 'POST'])
def instance(instance_id):
	app_collection = appDb.get_collection(str(instance_id))
	
	if request.method == 'POST':
		document = util.create_document(request.get_json())
		# persist document
		post_id = app_collection.insert_one(document).inserted_id
		app_collection.create_index([("timestamp", pymongo.ASCENDING)])
		
		return make_response(jsonify(document_id=str(post_id),instance_id=instance_id), status.HTTP_201_CREATED)

	app_collection = appDb.get_collection(str(instance_id))
	col_info_response = {
		"full_name": app_collection.full_name,
		"aprox_doc_count": app_collection.estimated_document_count(maxTimeMS=5000)
	}
	return make_response(jsonify(col_info_response), status.HTTP_200_OK )


@app.route("/instances")
def list_instances():
	collection_list = appDb.list_collection_names()
	return jsonify(collection_list)
"""


@app.route("/<uuid:instance_id>/head")
def find_head(instance_id):
	"""
	Gets the latest document of the instance collection
	"""
	app_collection = appDb.get_collection(str(instance_id))
	latest_document = app_collection.find().sort('timestamp', pymongo.DESCENDING).limit(1)
	return make_response(util.dumps(latest_document), status.HTTP_200_OK)


@app.route("/<uuid:instance_id>/first")
def find_first(instance_id):
	"""
	Gets the first document of the instance collection
	"""
	app_collection = appDb.get_collection(str(instance_id))
	first_document = app_collection.find().sort('timestamp', pymongo.ASCENDING).limit(1)
	return make_response(util.dumps(first_document), status.HTTP_200_OK)


@app.route("/<uuid:instance_id>/first/<int:number_of_documents>")
def get_first_documents(instance_id, number_of_documents):
	"""
	Lists the first n documents, from oldest to newest.
	TODO: Same as history/first. Check if we should change this.
	"""
	if number_of_documents > 1000:
		number_of_documents = 1000
	app_collection = appDb.get_collection(str(instance_id))
	history_documents = app_collection.find().sort('timestamp', pymongo.ASCENDING).limit(number_of_documents)
	return make_response(util.dumps(history_documents), status.HTTP_200_OK)
"""
#	==============================================================================================================
#	BELOW THIS = MOVED TO HISTORY BLUEPRINT
#	==============================================================================================================
"""
@app.route("/<uuid:instance_id>/history")
def get_history(instance_id):
	"""
	Lists the last 100 documents from the history, from most recent to oldest.
	"""
	first = request.args.get('first', default=-1, type = int)
	last = request.args.get('last', default=-1, type = int)

	return make_response(str(first) + "___" + str(last), status.HTTP_200_OK)


@app.route("/<uuid:instance_id>/history/first/<int:number_of_documents>")
def get_history_since(instance_id, number_of_documents):
	"""
	Lists the first n documents, from oldest to newest.
	"""
	app_collection = appDb.get_collection(str(instance_id))
	history_documents = app_collection.find().sort('timestamp', pymongo.ASCENDING).limit(number_of_documents)
	return make_response(util.dumps(history_documents), status.HTTP_200_OK)


@app.route("/<uuid:instance_id>/history/last/<int:limit>")
def get_history_until(instance_id, limit):
	"""
	Lists the last n documents, from most recent to the oldest. There is a hard limit of 1000 (one thousand) documents.
	TODO: test if we should do this or just use the current contract.
	"""
	return status.HTTP_204_NO_CONTENT


if __name__ == "__main__":
	app.run()

