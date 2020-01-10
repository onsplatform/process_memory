from process_memory.db import *
from process_memory.header import Header
import datetime

connect('platform_memory')


class Map(DynamicDocument):
    header = EmbeddedDocumentField(Header)
    id = UUIDField(binary=False)
    name = StringField()
    processId = UUIDField(binary=False)
    systemId = UUIDField(binary=False)
    content = DictField()
