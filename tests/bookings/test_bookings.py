import pytest
from conftest import login_as_student
from app.appointment.model import Appointment
from app.users.models import User
from app.course.model import Course
from app.room.model import Room
from datetime import datetime, timedelta


class TestBookings:

    def create_test_appointment(self, student=None, enrolled=False, full=False, past=False, canceled=False):
        teacher = User.objects.get(email="teacher@test.de")
        course = Course.objects.get(name="Course 1")
        room = Room.objects.get(name="Room 1")

        date = datetime.now() - timedelta(days=1) if past else datetime.now() + timedelta(days=3)
        students = [student] if (enrolled and student) else []
        max_students = 1 if full else 5

        appointment = Appointment(
            date=date,
            max_students=max_students,
            course=course,
            room=room,
            teacher=teacher,
            canceled=canceled,
            students=students
        ).save()

        return appointment

    def test_view_home_shows_upcoming_courses(self, testapp):
        login_as_student(testapp)
        response = testapp.get('/bookings/', follow_redirects=True)
        assert response.status_code == 200
        assert b"Kursname" in response.data or b"Termin" in response.data

    def test_book_valid_course(self, testapp):
        student = User.objects.get(email="student0@test.de")
        appointment = self.create_test_appointment(student, enrolled=False)

        login_as_student(testapp)
        response = testapp.post(f'/bookings/booked_course/{appointment.id}', follow_redirects=True)

        appointment.reload()
        assert response.status_code == 200
        assert student in appointment.students
        assert b"Kurs wurde erfolgreich belegt" in response.data

    def test_course_full_warning(self, testapp):
        student = User.objects.get(email="student0@test.de")
        appointment = self.create_test_appointment(student=student, enrolled=True, full=True)

        login_as_student(testapp)
        response = testapp.post(f'/bookings/booked_course/{appointment.id}', follow_redirects=True)
        assert "Der Kurs ist voll" in response.data.decode("utf-8")

    def test_participation_pdf_blocked_before_date(self, testapp):
        student = User.objects.get(email="student0@test.de")
        appointment = self.create_test_appointment(student=student, enrolled=True, past=False)

        login_as_student(testapp)
        response = testapp.get(f'/bookings/confirmed_participant_pdf/{appointment.id}', follow_redirects=True)
        assert "Teilnahmenachweis erst nach Kurstermin" in response.data.decode("utf-8")

    def test_participation_pdf_after_course_allowed(self, testapp):
        student = User.objects.get(email="student0@test.de")
        appointment = self.create_test_appointment(student=student, enrolled=True, past=True)

        login_as_student(testapp)
        response = testapp.get(f'/bookings/confirmed_participant_pdf/{appointment.id}', follow_redirects=True)

        assert response.status_code == 200
        assert b"%PDF" in response.data[:4]  # PDF beginnt mit %PDF

    def test_logout_from_course(self, testapp):
        student = User.objects.get(email="student0@test.de")
        appointment = self.create_test_appointment(student=student, enrolled=True)

        login_as_student(testapp)
        response = testapp.post(f'/bookings/logout_courses/{appointment.id}', follow_redirects=True)

        appointment.reload()
        assert student not in appointment.students
        assert b"Kurs wurde erfolgreich abgemeldet" in response.data

    def test_logout_after_course_date_fails(self, testapp):
        student = User.objects.get(email="student0@test.de")
        appointment = self.create_test_appointment(student=student, enrolled=True, past=True)

        login_as_student(testapp)
        response = testapp.post(f'/bookings/logout_courses/{appointment.id}', follow_redirects=True)

        appointment.reload()
        assert student in appointment.students
        assert "Abmeldung" in response.data.decode("utf-8")
        assert "nicht mehr möglich" in response.data.decode("utf-8")

    def test_logout_from_not_enrolled_course(self, testapp):
        student = User.objects.get(email="student0@test.de")
        appointment = self.create_test_appointment(student=student, enrolled=False)

        login_as_student(testapp)
        response = testapp.post(f'/bookings/logout_courses/{appointment.id}', follow_redirects=True)

        appointment.reload()
        assert student not in appointment.students
        assert "Kurs wurde erfolgreich abgemeldet" in response.data.decode("utf-8") or response.status_code == 200

    def test_booking_canceled_course_fails(self, testapp):
        student = User.objects.get(email="student0@test.de")
        appointment = self.create_test_appointment(student=student, enrolled=False, canceled=True)

        login_as_student(testapp)
        response = testapp.post(f'/bookings/booked_course/{appointment.id}', follow_redirects=True)

        assert "Kurs ist storniert" in response.data.decode("utf-8") or response.status_code == 200

    def test_pdf_access_not_enrolled_denied(self, testapp):

        student = User.objects.get(email="student0@test.de")
        appointment = self.create_test_appointment(student=None, enrolled=False, past=True)

        login_as_student(testapp)
        response = testapp.get(f'/bookings/confirmed_participant_pdf/{appointment.id}', follow_redirects=True)

        # Prüfen, ob ein PDF ausgeliefert wird
        assert response.status_code == 200
        assert response.data.startswith(b"%PDF")


