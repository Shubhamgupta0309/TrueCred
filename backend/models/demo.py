from mongoengine import Document, StringField, IntField

class DemoDocument(Document):
    meta = {'collection': 'demo_collection'}
    name = StringField(required=True)
    value = IntField(required=True)