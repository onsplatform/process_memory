########################################################################################################################
#   Map Schema Validation - Model
########################################################################################################################

from mongoengine import *
from process_memory.models import Header


class Map(Document):
    header = EmbeddedDocumentField(Header)
    id = UUIDField(binary=False, primary_key=True, required=True)
    name = StringField()
    processId = UUIDField(binary=False)
    systemId = UUIDField(binary=False)
    content = DictField()
    _metadata = DictField()
