from mongoengine import *
import datetime

class Data(Document):
    nome = StringField(max_length=200, required=True)
    date_modified = DateTimeField(default=datetime.datetime.utcnow)
    meta = {'collection': 'collection_name'}


# GridFS Support from MongoEngine
'''
class Animal(Document):
    genus = StringField()
    family = StringField()
    photo = FileField()

marmot = Animal(genus='Marmota', family='Sciuridae')

marmot_photo = open('marmot.jpg', 'rb')
marmot.photo.put(marmot_photo, content_type = 'image/jpeg')
marmot.save()
'''

# GridFS Retrieval
'''
marmot = Animal.objects(genus='Marmota').first()
photo = marmot.photo.read()
content_type = marmot.photo.content_type
'''