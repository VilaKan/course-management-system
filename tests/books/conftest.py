import pytest

from app.factory import create_app
from app.books.model import Book
from app.users.models import User
from werkzeug.security import generate_password_hash


@pytest.fixture()
def testapp():
    app = create_app('app.config.TestingConfig')
    client = app.test_client()

    # add admin account
    admin = User(username="admin@test.de", password=generate_password_hash("test"))
    admin.save()

    # clear data base
    Book.objects().delete()

    return client


@pytest.fixture()
def test_entry():
    """
    create test entry
    """
    return Book(title="Testbook", author='Testauthor', year=2021)
