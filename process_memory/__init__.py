import os
from mongoengine import connect
import pymongo
from flask import Flask

app = Flask(__name__)

connect(
    db='process_memory',
    username='dbadmin',
    password='T4FbKpQoURhrilE7',
    host='docdb-jmi5t.mongodb.net/test?retryWrites=true'

)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(

    )

@app.route("/")
def hello():
	client = pymongo.MongoClient("mongodb+srv://dbadmin:T4FbKpQoURhrilE7@docdb-jmi5t.mongodb.net/test?retryWrites=true")
	db = client.test
	return "Hello, World" + str(db)

'''
@app.route("/create")
@app.route("/commit")
@app.route("/head")
@app.route("/history")
@app.route("/first")
@app.route("/history_last")
@app.route("/history_first")
@app.route("/first_and_last")

@app.route("/clone")
@app.route("/event")
# This is like a table inside a database
@app.route("/getcollection")
@app.route("/putcollection")

A API atual o id da coleção é passado direto pela URL.
@app.route("/collection_num/create")
'''