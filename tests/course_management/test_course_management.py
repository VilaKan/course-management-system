from tests.conftest import login_as_admin
from app.course.model import Course

class TestCourseManagement:
    def test_course_list_requires_login(self, testapp):
        """Kursliste ist nur nach Login sichtbar"""
        rv = testapp.get('/course_list/')
        assert rv.status_code == 302
        assert '/login' in rv.headers['Location']

    def test_course_list_visible_after_login(self, testapp):
        """Kursliste lädt erfolgreich nach Login"""
        login_as_admin(testapp)
        rv = testapp.get('/course_list/')
        assert rv.status_code == 200
        assert 'Kursliste' in rv.get_data(as_text=True)

    def test_course_create_form_visible(self, testapp):
        """Kurs erstellen Seite ist sichtbar"""
        login_as_admin(testapp)
        rv = testapp.get('/course_list/create')
        assert rv.status_code == 200
        assert 'Neuen Kurs anlegen' in rv.get_data(as_text=True)

    def test_course_create_success(self, testapp):
        """Kurs wird erfolgreich erstellt und taucht in Liste auf"""
        login_as_admin(testapp)
        rv = testapp.post('/course_list/create', data={
            'name': 'Testkurs 999',
            'description': 'Testbeschreibung für Kurs 999'
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'Testkurs 999' in rv.get_data(as_text=True)

    def test_course_edit_form_visible(self, testapp):
        """Kurs bearbeiten Seite ist sichtbar"""
        login_as_admin(testapp)
        course = Course(name='Editkurs 123', description='Beschreibung').save()
        rv = testapp.get(f'/course_list/edit/{str(course.id)}')
        assert rv.status_code == 200
        assert 'Kurs bearbeiten' in rv.get_data(as_text=True)

    def test_course_edit_submit_success(self, testapp):
        """Kurs wird erfolgreich bearbeitet"""
        login_as_admin(testapp)
        course = Course(name='Änderkurs', description='Alt').save()
        rv = testapp.post(f'/course_list/edit/{str(course.id)}', data={
            'name': 'Geänderter Kursname',
            'description': 'Neue Beschreibung'
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'Geänderter Kursname' in rv.get_data(as_text=True)

    def test_course_create_empty_fields(self, testapp):
        """Fehleranzeige bei leeren Eingabefeldern beim Erstellen"""
        login_as_admin(testapp)
        rv = testapp.post('/course_list/create', data={
            'name': '',
            'description': ''
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'dürfen nicht leer sein' in rv.get_data(as_text=True)

    def test_course_create_duplicate_name(self, testapp):
        """Fehler bei Erstellung mit bereits vorhandenem Kursnamen"""
        login_as_admin(testapp)
        Course(name='Kollision', description='Test 1').save()
        rv = testapp.post('/course_list/create', data={
            'name': 'Kollision',
            'description': 'Anderer Inhalt'
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'existiert bereits' in rv.get_data(as_text=True)

    def test_course_edit_empty_fields(self, testapp):
        """Fehleranzeige bei leerem Namen/Beschreibung beim Bearbeiten"""
        login_as_admin(testapp)
        course = Course(name='Bearbeitbar', description='Bearbeiten').save()
        rv = testapp.post(f'/course_list/edit/{str(course.id)}', data={
            'name': '',
            'description': ''
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'dürfen nicht leer sein' in rv.get_data(as_text=True)
