########################################################################################################################
#   Map Schema Validation - Model
########################################################################################################################


from mongoengine import *
from process_memory.models.header import Header


class Map(Document):
    header = EmbeddedDocumentField(Header)
    id = UUIDField(binary=False)
    name = StringField()
    processId = UUIDField(binary=False)
    systemId = UUIDField(binary=False)
    content = DictField()
    _metadata = DictField()
