from datetime import datetime
from bson.json_util import dumps

def create_document(body):
	'''	Prepare document for persistance.'''
	header = {"timestamp": datetime.utcnow()}
	return {**header, **body}