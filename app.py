from flask import Flask,request, jsonify, make_response
from flask_api import status
import pymongo
import util


app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://dbadmin:T4FbKpQoURhrilE7@docdb-jmi5t.mongodb.net/test?retryWrites=true")
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
	Gets the lastest document of the instance collection
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





if __name__ == "__main__":
	app.run()

