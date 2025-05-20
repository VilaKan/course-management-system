from app.database import db

class Course(db.Document):
    name = db.StringField(required=True)
    description = db.StringField(required=True)