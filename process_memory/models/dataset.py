########################################################################################################################
#   Dataset Schema Validation - Model
########################################################################################################################

from mongoengine import *

from process_memory.models import BaseDynamicDocument
from process_memory.models import Header
import datetime



class Dataset(DynamicDocument):
    """
    Dataset of entities. Only required field is the Header document.
    """
    header = EmbeddedDocumentField(Header)
    entities = DictField()
