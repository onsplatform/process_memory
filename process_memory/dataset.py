########################################################################################################################
#   Schema Validation
########################################################################################################################

from mongoengine import *
import datetime

connect('platform_memory')


class Header(DynamicEmbeddedDocument):
    """
    This is the main header document that should be referenced in all related data.
    """
    timestamp = DateTimeField(default=datetime.datetime.utcnow())
    processId = UUIDField(Required=True, binary=False)
    systemId = UUIDField(Required=True, binary=False)
    instanceId = UUIDField(Required=True, binary=False)
    eventOut = StringField(Required=False)
    commit = BooleanField(Required=False)


class Usina(DynamicDocument):
    """
    Contains basic information that should be saved. It´s dynamic for future data that may be added.
    """
    #header = DynamicEmbeddedDocument(Header)
    data = DictField()
    """
        idusina = StringField(max_length=20)
    tipousina = StringField(max_length=20)
    nomecurto = StringField(max_length=50)
    dataentradaoperacao = DateTimeField()
    datapropagadaconcessaogeracao = DateTimeField()
    id = UUIDField(required=True, binary=False)
    metadata = DictField()
    """


class UnidadeGeradora(DynamicDocument):
    """
    Contains information about generator units. These are related to Usina.
    """
    iduge = StringField(max_length=20)
    idequipamento = StringField(max_length=20)
    idtipoequipamento = StringField(max_length=10)
    idusina = StringField(max_length=20)
    idtipouge = StringField(max_length=10)
    idagenteproprietario = StringField(max_length=10)
    dataentradaoperacao = DateTimeField()
    idoons = StringField(max_length=20)
    id = UUIDField(required=True)
    metadata = DictField()


class PotenciaUge(DynamicDocument):
    """
    Information about power generation. This is related to UnidadeGeradora.
    """
    datainicio = DateTimeField()
    idpotenciaindisponibilidade = IntField()
    iduge = StringField(max_length=20)
    valorpotencia = FloatField()
    id = UUIDField(required=True, binary=False)
    metadata = DictField()


class FranquiaUge(DynamicDocument):
    dataatualizacaosaldo = DateTimeField()
    idconsolidacaomensal = UUIDField(binary=False)
    iduge = StringField(max_length=20)
    origemfranquia = StringField(max_length=10)
    saldofranquia = DecimalField(precision=8)
    tempouso = DecimalField(precision=8)
    limiteutilizacao = DecimalField(precision=8)
    id = UUIDField(binary=False)
    metadata = DictField()


class EventoMudancaEstadoOperativo(DynamicDocument):
    id = UUIDField(binary=False)


class Entities(DynamicEmbeddedDocument):
    usina = ListField(ReferenceField(Usina))
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
