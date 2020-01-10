import datetime
from mongoengine import DynamicEmbeddedDocument, DateTimeField, UUIDField, StringField, BooleanField


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