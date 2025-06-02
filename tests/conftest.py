import pytest

from app.factory import create_app, create_rooms, create_roles, create_users, create_courses, create_appointments
from mongoengine.connection import get_connection


@pytest.fixture(scope='session')
def testapp(request):
    # setup
    app = create_app('app.config.TestingConfig')
    client = app.test_client()
    setup_db()
    yield client

    # teardown
    drop_testing_database()


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
    conn = get_connection()  # Gets the current pymongo.MongoClient
    conn.drop_database('testing')