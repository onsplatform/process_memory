from datetime import datetime
import snappy
import json
from bson import json_util


def get_time():
	return datetime.utcnow()


def create_document(body):
	"""	Prepare document for persistance."""
	header = {"timestamp": datetime.utcnow()}
	return {**header, **body}


def include_header(header, body):
	timestamped_header = {"header": header}
	timestamped_header.update({"timestamp": datetime.utcnow()})
	return {**timestamped_header, **body}


def prepare_document(body, **kwargs):
	"""	Prepare document for persistance."""
	header = {
		"timestamp": datetime.utcnow(),
		"instance_id": "instance_id"
	}
	return {**header, **body}


def compress(data: bytes):
	"""
	Compresses data with default encoding UTF-8. We currently use Google´s Snappy (it´s fast).
	:param data: bytes that are going to be compressed.
	:return: bytes compressed by algorithm.
	"""
	return snappy.compress(data, 'utf-8')


def uncompress(data: bytes):
	"""
	Uncompresses data from repository. Using Google´s Snappy (it´s very fast).
	:param data: bytes that have been compressed
	:return: bytes decompressed by algorithm.
	"""
	return snappy.uncompress(data)


def convert_to_bytes(dictionary_data: dict):
	"""
	Receives a dictionary data and converts to an UTF-8, BSON compatible bytes array.
	:param dictionary_data: An object in the form of a dictionary.
	:return: bytes encoded in UTF-8 and BSON compatible.
	"""
	return json.dumps(dictionary_data, default=json_util.default).encode('utf-8')
