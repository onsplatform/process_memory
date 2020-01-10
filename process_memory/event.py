from process_memory.db import *
from process_memory.header import Header
import datetime


connect('platform_memory')


class BaseDynamicDocument(DynamicDocument):
    meta = {'abstract': True}
    header = EmbeddedDocumentField(Header)
    data = DictField()


class Registros(BaseDynamicDocument):
    timestamp = DateTimeField(default=datetime.datetime.utcnow())


class RegistrosOcorrencia(DynamicDocument):
    registros = ListField(ReferenceField(Registros))


class Eventos(BaseDynamicDocument):
    timestamp = DateTimeField(default=datetime.datetime.utcnow())


class Payload(DynamicDocument):
    idconfiguracaocenario = UUIDField(binary=False)
    configuracaocenario = DictField()
    origensserializa = DictField()
    registrosocorrencia = EmbeddedDocumentField(RegistrosOcorrencia)
    idsuges = DictField()
    eventos = ListField(ReferenceField(Eventos))


class Event(DynamicDocument):
    header = EmbeddedDocumentField(Header)
    name = StringField(required=False)
    scope = StringField(required=False)
    instanceId = UUIDField(binary=False)
    timestamp = DateTimeField(required=False)
    owner = StringField(required=False)
    tag = UUIDField(binary=False)
    branch = StringField(required=False)
    reproduction = DictField()
    reprocessing = DictField()
    payload = EmbeddedDocumentField(Payload)
