from datetime import datetime


def create_document(body):
	"""	Prepare document for persistance."""
	header = {"timestamp": datetime.utcnow()}
	return {**header, **body}
