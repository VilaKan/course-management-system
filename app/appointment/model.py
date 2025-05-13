from flask_mongoengine import MongoEngine

db = MongoEngine()

class Appointment(db.Document):
    id = db.IntField(required=True, primary_key=True)
    date = db.DateField(required=True)
    max_students = db.IntField(required=True)
    course = db.IntField(required=True)
    room = db.IntField(required=True)
    teacher = db.IntField(required=True)
    students = db.ListField(required=True)