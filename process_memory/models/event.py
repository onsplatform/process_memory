########################################################################################################################
#   Event Schema Validation - Model
########################################################################################################################

from mongoengine import *
from process_memory.models.header import Header
import datetime


class BaseDynamicDocument(DynamicDocument):
    meta = {'abstract': True}
    header = EmbeddedDocumentField(Header)
    data = DictField()


class Eventos(BaseDynamicDocument):
    timestamp = DateTimeField(default=datetime.datetime.utcnow())


class Registros(BaseDynamicDocument):
    timestamp = DateTimeField(default=datetime.datetime.utcnow())


class RegistrosOcorrencia(DynamicEmbeddedDocument):
    registros = ListField(ReferenceField(Registros))


class Payload(DynamicEmbeddedDocument):
    idconfiguracaocenario = UUIDField(binary=False)
    configuracaocenario = DictField()
    origensserializa = DictField()
    idsuges = DictField()
    registrosocorrencia = EmbeddedDocumentField(RegistrosOcorrencia)
    eventos = ListField(ReferenceField(Eventos))


class Event(DynamicDocument):
    header = EmbeddedDocumentField(Header)
    name = StringField(required=False)
    scope = StringField(required=False)
    instanceId = UUIDField(binary=False)
    timestamp = StringField(required=False)
    owner = StringField(required=False)
    tag = UUIDField(binary=False)
    branch = StringField(required=False)
    reproduction = DictField()
    reprocessing = DictField()
    payload = EmbeddedDocumentField(Payload)
