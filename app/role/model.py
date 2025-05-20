from app.database import db

class Role(db.Document):
    name = db.StringField(max_length=80, required=True)
