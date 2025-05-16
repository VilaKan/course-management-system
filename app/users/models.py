from flask_mongoengine import MongoEngine
from flask_login import UserMixin

db = MongoEngine()


class User(db.Document, UserMixin):
    id = db.IntField(required=True, primary_key=True)
    username = db.StringField(required=True)
    email = db.EmailField(required=True)
    password = db.StringField(required=True)
    role = db.IntField(required=True)
    date_of_birth = db.DateField(required=True)

    def __repr__(self):
        return '<User %r>' % self.id
