from datetime import datetime


def create_document(body):
	"""	Prepare document for persistance."""
	header = {"timestamp": datetime.utcnow()}
	return {**header, **body}


def prepare_document(body, **kwargs):
	"""	Prepare document for persistance."""
	header = {
		"timestamp": datetime.utcnow(),
		"instance_id": "instance_id"
	}
	return {**header, **body}

"""
TODO: criar um cabeçalho único para os documentos. O cabeçalho será responsável pelo match dentro do MongoDB
TODO: criar método para extração de json para cada coleção. Vamos receber um único json com vários documentos.

	"processId": "4c7735de-6992-4c1a-ab73-e4114b2da42a",
	"systemId": "a22d9e4d-c352-4ac2-8321-2c496fe3a116",
	"instanceId": "c1996da1-ae96-4e99-9b80-bec749d2d67c",
	"eventOut": "confirmar.estruturacao.cenario.request.done",
	"commit": true
"""