from flask import Flask,Request,Response
import pymongo

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
	Creates a collection to host the app instance
	'''
	if Request.method == 'POST':
		# check if exists. if not, create collection and insert a document to start collection at mongodb.
		#client.
		collectionList = appDb.list_collection_names()
		return "There is a collection: " + str(collectionList)
	
	
	return str(instance_id)

if __name__ == "__main__":
	app.run()

@app.route("/instances")
def listInstances():
	collectionList = appDb.list_collection_names()
	return collectionList
