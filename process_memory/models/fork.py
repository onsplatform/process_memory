########################################################################################################################
#   Fork Schema Validation - Model
########################################################################################################################

from mongoengine import *
from process_memory.models import Header


class Fork(DynamicDocument):
    header = EmbeddedDocumentField(Header)
    name = UUIDField(binary=False)
    description = StringField()
    startedAt = StringField()
    status = StringField()
    owner = StringField()
