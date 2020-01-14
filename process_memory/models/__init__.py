from process_memory.db import *
from process_memory.models.header import Header

connect('platform_memory')


class BaseDynamicDocument(DynamicDocument):
    meta = {'abstract': True}
    header = EmbeddedDocumentField(Header)
    data = DictField()
