from flask_mongoengine import MongoEngine

db = MongoEngine()

class Role(db.Document):
    id = db.IntField(required=True, primary_key=True)
    name = db.StringField(max_length=80, required=True)