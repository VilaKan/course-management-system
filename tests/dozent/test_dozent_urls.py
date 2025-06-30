#! ../env/bin/python
# -*- coding: utf-8 -*-
from tests.conftest import testapp, login_as_teacher

class TestDozentURLs:
    def test_dozent_logged_out(self, testapp):
        """Testet, ob /dozent/ redirectet wenn ausgeloggt"""
        rv = testapp.get('/dozent/', follow_redirects=False)
        assert rv.status_code == 302

    def test_dozent_logged_in(self, testapp):
        """Testet, ob /dozent/ mit Teacher erfolgreich lädt"""
        login_as_teacher(testapp)
        rv = testapp.get('/dozent/')
        assert rv.status_code == 200

    def test_teilnehmerliste_post(self, testapp):
        """Testet POST an /dozent/teilnehmerliste mit gültiger appointment_id"""
        login_as_teacher(testapp)

        from app.appointment.model import Appointment
        appointment = Appointment.objects.first()

        rv = testapp.post('/dozent/teilnehmerliste', data={
            'appointment_id': str(appointment.id)
        })
        assert rv.status_code == 200

    def test_no_appointments_shows_message(self, testapp):
        """Testet, ob Nachricht erscheint, wenn keine Termine vorhanden sind"""
        login_as_teacher(testapp)

        from app.appointment.model import Appointment
        Appointment.objects.delete()

        rv = testapp.get('/dozent/')
        assert "Keine Termine gefunden." in rv.data.decode("utf-8")

    def test_filter_with_no_results(self, testapp):
        """Testet, ob Nachricht erscheint, wenn keine Termine im Zeitraum liegen"""
        login_as_teacher(testapp)

        from app.appointment.model import Appointment
        import datetime

        appointment = Appointment.objects.first()
        if not appointment:
            return

        appointment.date = datetime.date(2025, 1, 1)
        appointment.save()

        rv = testapp.post('/dozent/', data={
            'start_date': '2025-02-01',
            'end_date': '2025-02-02'
        })

        html = rv.data.decode("utf-8")
        assert "Keine Termine im gewählten Zeitraum gefunden." in html

    def test_teilnehmerliste_keine_teilnehmer(self, testapp):
        """Testet, ob Nachricht erscheint, wenn keine Teilnehmer im Termin sind"""
        login_as_teacher(testapp)

        from app.appointment.model import Appointment
        appointment = Appointment.objects.first()
        if appointment:
            appointment.students = []
            appointment.save()

            rv = testapp.post('/dozent/teilnehmerliste', data={
                'appointment_id': str(appointment.id)
            })
            html = rv.data.decode("utf-8")
            assert "Für diesen Termin sind keine Teilnehmer angemeldet." in html
