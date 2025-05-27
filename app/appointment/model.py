from app.database import db
from mongoengine.fields import ReferenceField, ListField
from mongoengine import NULLIFY


class Appointment(db.Document):
    date = db.DateField(required=True)
    max_students = db.IntField(required=True)
    course = ReferenceField("Course", reverse_delete_rule=NULLIFY, required=True)
    room = ReferenceField("Room", required=True, reverse_delete_rule=NULLIFY)
    teacher = ReferenceField("User", required=True, reverse_delete_rule=NULLIFY)
    students = ListField(ReferenceField("User", reverse_delete_rule=NULLIFY))
    canceled = db.BooleanField(default=False, required=True)