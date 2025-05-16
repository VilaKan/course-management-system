from flask_mongoengine import MongoEngine

db = MongoEngine()

class Course(db.Document):
    id = db.IntField(required=True, primary_key=True)
    name = db.StringField(required=True)
    description = db.StringField(required=True)