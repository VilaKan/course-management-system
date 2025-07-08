import pytest
from app.factory import create_app, create_rooms, create_roles, create_users, create_courses, create_appointments
from mongoengine.connection import get_connection


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

def drop_testing_database():
    conn = get_connection()
    conn.drop_database('testing')

def login_as_admin(testapp):
    return testapp.post('/login', data={
        'username': 'admin@test.de',
        'password': 'test'
    }, follow_redirects=True)

def login_as_teacher(testapp):
    return testapp.post('/login', data={
        'username': 'teacher@test.de',
        'password': 'test'
    }, follow_redirects=True)

def login_as_student(testapp):
    return testapp.post('/login', data={
        'username': 'student0@test.de',
        'password': 'test'
    }, follow_redirects=True)
