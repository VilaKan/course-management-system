import pytest
from app.factory import create_app, create_rooms, create_roles, create_users, create_courses, create_appointments
from mongoengine.connection import get_connection
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture(scope='session')
def testapp():
    app = create_app('app.config.TestingConfig')
    client = app.test_client()
    drop_testing_database()
    setup_db()

    yield client

def setup_db():
    create_rooms()
    create_roles()
    create_users()
    create_courses()
    create_appointments()

def login_as_admin(testapp):
    rv = testapp.post('/login', data=dict(
        username='admin@test.de',
        password="test"
    ), follow_redirects=True)

    return rv

def login_as_teacher(testapp):
    rv = testapp.post('/login', data=dict(
        username='teacher@test.de',
        password="test"
    ), follow_redirects=True)

    return rv

def login_as_student(testapp):
    rv = testapp.post('/login', data=dict(
        username='student0@test.de',
        password="test"
    ), follow_redirects=True)

    return rv

def drop_testing_database():
    conn = get_connection()
    conn.drop_database('testing')