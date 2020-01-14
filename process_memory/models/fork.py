########################################################################################################################
#   Fork Schema Validation - Model
########################################################################################################################

from mongoengine import *


class Fork(DynamicDocument):
    name = UUIDField(binary=False)
    description = StringField()
    startedAt = StringField()
    status = StringField()
    owner = StringField()
