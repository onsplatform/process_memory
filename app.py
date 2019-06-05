from flask import Flask,request, jsonify, make_response
from flask_api import status
import pymongo
import util


app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://dbadmin:T4FbKpQoURhrilE7@docdb-jmi5t.mongodb.net")
appDb = client["process_memory"]


@app.route("/")
def testConnection():	
	db = client.test
	return str(db)

@app.route("/instances/<uuid:instance_id>", methods = ['GET', 'POST'])
def instance(instance_id):	
	'''
	Creates a collection and inserts a document to host the app instance.
	TODO: create better comments for auto-documentation
	'''
	appCollection = appDb.get_collection(str(instance_id))
	
	if request.method == 'POST':
		document = util.create_document(request.get_json())
		# persist document
		post_id = appCollection.insert_one(document).inserted_id
		appCollection.create_index([("timestamp", pymongo.ASCENDING)])
		
		return make_response(jsonify(document_id=str(post_id),instance_id=instance_id), status.HTTP_201_CREATED)
	else:
		appCollection = appDb.get_collection(str(instance_id))
		colInfoResponse = {
			"full_name": appCollection.full_name,
			"aprox_doc_count": appCollection.estimated_document_count(maxTimeMS=5000)
		}
		return make_response(jsonify(colInfoResponse), status.HTTP_200_OK )

@app.route("/instances")
def listInstances():
	collectionList = appDb.list_collection_names()
	return jsonify(collectionList)

@app.route("/<uuid:instance_id>/head")
def findHead(instance_id):
	'''
	Gets the latest document of the instance collection
	'''
	appCollection = appDb.get_collection(str(instance_id))
	latestDocument = appCollection.find().sort('timestamp', pymongo.DESCENDING).limit(1)
	return make_response(util.dumps(latestDocument), status.HTTP_200_OK)

@app.route("/<uuid:instance_id>/first")
def findFirst(instance_id):
	'''
	Gets the first document of the instance collection
	'''
	appCollection = appDb.get_collection(str(instance_id))
	firstDocument = appCollection.find().sort('timestamp', pymongo.ASCENDING).limit(1)
	return make_response(util.dumps(firstDocument), status.HTTP_200_OK)

@app.route("/<uuid:instance_id>/first/<int:number_of_documents>")
def getFirstDocuments(instance_id, number_of_documents):
	'''
	Lists the first n documents, from oldest to newest.
	TODO: Same as history/first. Check if we should change this.
	'''
	if number_of_documents > 1000:
		number_of_documents = 1000
	appCollection = appDb.get_collection(str(instance_id))
	historyDocuments = appCollection.find().sort('timestamp', pymongo.ASCENDING).limit(number_of_documents)
	return make_response(util.dumps(historyDocuments), status.HTTP_200_OK)

@app.route("/<uuid:instance_id>/history")
def getHistory(instance_id):
	'''
	Lists the last 1000 documents from the history, from most recent to oldest.
	'''
	first = request.args['first']
	last = request.args['last']
	print(first)
	print(last)
	return make_response(str(first) + "___" + str(last),status.HTTP_200_OK) 

@app.route("/<uuid:instance_id>/history/first/<int:number_of_documents>")
def getHistorySince(instance_id, number_of_documents):
	'''
	Lists the first n documents, from oldest to newest.
	'''
	appCollection = appDb.get_collection(str(instance_id))
	historyDocuments = appCollection.find().sort('timestamp', pymongo.ASCENDING).limit(number_of_documents)
	return make_response(util.dumps(historyDocuments), status.HTTP_200_OK)


@app.route("/<uuid:instance_id>/history/last/<int:limit>")
def getHistoryUntil(instance_id, limit):
	'''
	Lists the last n documents, from most recent to the oldest. There is a hard limit of 1000 (one thousand) documents.
	'''
	return status.HTTP_204_NO_CONTENT


if __name__ == "__main__":
	app.run()

