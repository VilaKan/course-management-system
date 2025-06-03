from flask_login import UserMixin
from mongoengine.fields import ReferenceField
from mongoengine import NULLIFY

from app.database import db


class User(db.Document, UserMixin):
    username = db.StringField(required=True)
    email = db.EmailField(required=True)
    password = db.StringField(required=True)
    role = ReferenceField('Role', required=True, reverse_delete_rule=NULLIFY)
    date_of_birth = db.DateField(required=True)
    is_active = db.BooleanField(default=True)

    def __repr__(self):
        return '<User %r>' % self.username
