import pytest

from app.factory import create_app
from app.users.models import User
from werkzeug.security import generate_password_hash


@pytest.fixture()
def testapp():
    app = create_app('app.config.TestingConfig')
    client = app.test_client()

    # add admin account
    #admin = User(username="admin@test.de", password=generate_password_hash("test"))
    #admin.save()


    return client
