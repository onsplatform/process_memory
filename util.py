from datetime import datetime
import snappy


def create_document(body):
	"""	Prepare document for persistance."""
	header = {"timestamp": datetime.utcnow()}
	return {**header, **body}


def include_header(header: dict, body):
	new_header = header
	new_header.update({"timestamp": datetime.utcnow()})
	return {**new_header, **body}


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
