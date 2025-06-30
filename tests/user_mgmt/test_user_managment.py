from app.role.model import Role
from app.users.models import User
from tests.conftest import testapp, login_as_admin, login_as_teacher
import datetime
from werkzeug.security import generate_password_hash


class TestUserManagement:

    def _create_test_user(self, username="testuser@test.de", role_name="User", is_active=True):
        role = Role.objects(name=role_name).first()
        user = User(
            username=username,
            email=username,
            password=generate_password_hash("secret123"),
            role=role,
            date_of_birth=datetime.datetime(2000, 1, 1),
            is_active=is_active
        )
        user.save()
        return user

    def test_home_redirect_if_not_logged_in(self, testapp):
        rv = testapp.get('/user_mgmt/', follow_redirects=False)
        assert rv.status_code == 302

    def test_home_logged_in(self, testapp):
        login_as_admin(testapp)
        rv = testapp.get('/user_mgmt/')
        assert rv.status_code == 200

    def test_create_user(self, testapp):
        login_as_admin(testapp)
        rv = testapp.post('/user_mgmt/add', data=dict(
            email="neuer_user@test.de",
            password="test1234",
            geburtsdatum="2000-01-01",
            role="User"
        ), follow_redirects=True)
        assert rv.status_code == 200
        assert b"erfolgreich angelegt" in rv.data

    def test_edit_user_email(self, testapp):
        login_as_admin(testapp)
        user = self._create_test_user("edituser@test.de")
        rv = testapp.post(f'/user_mgmt/edit/{user.id}', data=dict(
            email="edituser_new@test.de",
            password="",
            geburtsdatum="2000-01-01",
            role="User"
        ), follow_redirects=True)
        assert rv.status_code == 200
        assert b"erfolgreich aktualisiert" in rv.data

    def test_toggle_user_active(self, testapp):
        login_as_admin(testapp)
        user = self._create_test_user("activeuser@test.de", is_active=True)
        old_status = user.is_active
        rv = testapp.post(f'/user_mgmt/toggle_active/{user.id}', follow_redirects=True)
        user.reload()
        assert user.is_active != old_status

    def test_create_user_with_invalid_email(self, testapp):
        login_as_admin(testapp)
        rv = testapp.post('/user_mgmt/add', data=dict(
            email="ungültig",
            password="test1234",
            geburtsdatum="2000-01-01",
            role="User"
        ), follow_redirects=True)
        assert "Ungültige E-Mail-Adresse" in rv.data.decode("utf-8")

    def test_user_access_forbidden(self, testapp):
        login_as_teacher(testapp)
        rv = testapp.get('/user_mgmt/')
        assert rv.status_code in (302, 403)

    def test_deactivate_user(self, testapp):
        login_as_admin(testapp)
        user = self._create_test_user("deactivateuser@test.de", is_active=True)
        rv = testapp.post(f"/user_mgmt/deactivate/{user.id}", follow_redirects=True)
        user.reload()
        assert rv.status_code == 200
        assert not user.is_active
        assert b"deaktiviert" in rv.data

    def test_filter_user_by_role(self, testapp):
        login_as_admin(testapp)
        # Erstelle 2 Benutzer mit verschiedenen Rollen
        self._create_test_user("adminuser@test.de", role_name="Admin")
        self._create_test_user("normaluser@test.de", role_name="User")

        # Filtere nur Admins
        rv = testapp.get("/user_mgmt/?role=Admin")
        assert rv.status_code == 200
        html = rv.data.decode("utf-8")
        assert "adminuser@test.de" in html
        assert "normaluser@test.de" not in html

    def test_create_user_missing_fields(self, testapp):
        login_as_admin(testapp)
        rv = testapp.post("/user_mgmt/add", data=dict(
            email="",  # fehlt
            password="",  # fehlt
            geburtsdatum="",  # fehlt
            role=""  # fehlt
        ), follow_redirects=True)
        assert rv.status_code == 200
        assert "Bitte alle Pflichtfelder korrekt ausfüllen." in rv.data.decode("utf-8")

    def test_create_user_duplicate_email(self, testapp):
        login_as_admin(testapp)
        # Ersten User erstellen
        self._create_test_user("duplicate@test.de")
        # Versuch, denselben nochmals zu erstellen
        rv = testapp.post("/user_mgmt/add", data=dict(
            email="duplicate@test.de",
            password="test1234",
            geburtsdatum="2000-01-01",
            role="User"
        ), follow_redirects=True)
        assert rv.status_code == 200
        assert b"E-Mail existiert bereits" in rv.data or b"existiert bereits" in rv.data

    def test_create_user_weak_password(self, testapp):
        login_as_admin(testapp)
        rv = testapp.post("/user_mgmt/add", data=dict(
            email="weakpass@test.de",
            password="123",  # zu kurz
            geburtsdatum="2000-01-01",
            role="User"
        ), follow_redirects=True)
        assert rv.status_code == 200
        assert b"Pflichtfelder" in rv.data or b"Passwort" in rv.data
