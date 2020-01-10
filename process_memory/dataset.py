########################################################################################################################
#   Schema Validation
########################################################################################################################

from process_memory.db import *
from process_memory.header import Header
import datetime


connect('platform_memory')


class BaseDynamicDocument(DynamicDocument):
    meta = {'abstract': True}
    header = EmbeddedDocumentField(Header)
    data = DictField()


class UnidadeGeradora(BaseDynamicDocument):
    """
    Contains information about generator units. These are related to Usina.
    """
    timestamp = DateTimeField(default=datetime.datetime.utcnow())


class PotenciaUge(BaseDynamicDocument):
    """
    Information about power generation. This is related to UnidadeGeradora.
    """
    timestamp = DateTimeField(default=datetime.datetime.utcnow())


class FranquiaUge(BaseDynamicDocument):
    timestamp = DateTimeField(default=datetime.datetime.utcnow())


class EventoMudancaEstadoOperativo(BaseDynamicDocument):
    timestamp = DateTimeField(default=datetime.datetime.utcnow())


class Entities(DynamicEmbeddedDocument):
    """
    These are the entities that should have its own collection
    """
    unidadegeradora = ListField(ReferenceField(UnidadeGeradora))
    potenciauge = ListField(ReferenceField(PotenciaUge))
    franquiauge = ListField(ReferenceField(FranquiaUge))
    eventomudancaestadooperativo = ListField(ReferenceField(EventoMudancaEstadoOperativo))


class Dataset(DynamicDocument):
    """
    Dataset of entities. Only required field is the Header document.
    """
    header = EmbeddedDocumentField(Header)
    entities = EmbeddedDocumentField(Entities)
