import pytest

from app.factory import create_app
from app.users.models import User
from werkzeug.security import generate_password_hash


@pytest.fixture()
def testapp(request):
    app = create_app('app.config.TestingConfig')
    client = app.test_client()

    admin = User(username="admin", password=generate_password_hash("test"))
    admin.save()

    return client
