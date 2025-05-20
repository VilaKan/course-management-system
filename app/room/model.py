from app.database import db

class Room(db.Document):
    name = db.StringField(required=True)
