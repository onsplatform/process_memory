from process_memory.db import *
from process_memory.models.header import Header


class BaseDynamicDocument(DynamicDocument):
    meta = {'abstract': True}
    header = EmbeddedDocumentField(Header)
    data = DictField()
