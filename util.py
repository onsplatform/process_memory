import json
import pytz

from datetime import datetime
from bson import json_util


def get_time():
	return datetime.utcnow()


def convert_to_utc(date, format):
	date_validity = datetime.strptime(date, format)
	pst = pytz.timezone('Brazil/East')
	return pst.localize(date_validity)


def get_datetime_from(date_string: str, format='%Y-%m-%dT%H:%M:%S.%f'):
	if date_string:
		return datetime.strptime(date_string, format)

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


def convert_to_bytes(dictionary_data: dict):
	"""
	Receives a dictionary data and converts to an UTF-8, BSON compatible bytes array.
	:param dictionary_data: An object in the form of a dictionary.
	:return: bytes encoded in UTF-8 and BSON compatible.
	"""
	return json.dumps(dictionary_data, default=json_util.default).encode('utf-8')
