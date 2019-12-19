from mongoengine import *

connect('localhost')


class Metadata(DynamicEmbeddedDocument):
    content = DictField()


class Usina(Document):
    idusina = StringField(max_length=10)
    tipousina = StringField(max_length=10)
    nomecurto = StringField(max_length=50)
    dataentradaoperacao = DateTimeField()
    datapropagadaconcessaogeracao = DateTimeField()
    id = UUIDField(required=True)
    metadata = EmbeddedDocumentField(Metadata)


class Dataset(Document):
    agente = StringField(required=False)
    docs_embarcados = ListField(EmbeddedDocumentListField(Usina))
    usinas = ListField(ReferenceField(Usina))
