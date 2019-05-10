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
	Creates a collection to host the app instance.
	TODO: create better comments for auto-documentation
	'''
	if request.method == 'POST':
		# 
		appCollection = appDb[str(instance_id)]
		document = util.create_document(request.get_json())
		# persist document
		post_id = appCollection.insert_one(document).inserted_id
		
		return make_response(jsonify(document_id=str(post_id),instance_id=instance_id), status.HTTP_201_CREATED)
	else:
		appColInfo = appDb.get_collection(str(instance_id))
		colInfoResponse = {
			"full_name": appColInfo.full_name,
			"aprox_doc_count": appColInfo.estimated_document_count(maxTimeMS=5000)
		}
		return make_response(jsonify(colInfoResponse), status.HTTP_200_OK )

@app.route("/instances")
def listInstances():
	collectionList = appDb.list_collection_names()
	return jsonify(collectionList)

@app.route("/<uuid:instance_id>")
def teste(instance_id):
	return True


if __name__ == "__main__":
	app.run()

