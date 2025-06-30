import pytest
from datetime import datetime, timedelta
from app.role.model import Role
from app.users.models import User
from app.course.model import Course
from app.room.model import Room
from app.appointment.model import Appointment
from conftest import login_as_admin


def test_ft3_1a_admin_can_access_schedule(testapp):
    login_response = login_as_admin(testapp)
    assert login_response.status_code == 200

    response = testapp.get("/schedule_mgmt/")
    assert response.status_code == 200
    assert b"Termine verwalten" in response.data


def test_ft3_2a_create_valid_appointment(testapp):
    teacher = User.objects.get(email="teacher@test.de")
    course = Course.objects.get(name="Course 1")
    room = Room.objects.get(name="Room 1")

    login_response = login_as_admin(testapp)
    assert login_response.status_code == 200

    future_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

    response = testapp.post("/schedule_mgmt/", data={
        "datum": future_date,
        "kurs": str(course.id),
        "raum": str(room.id),
        "dozent": str(teacher.id),
        "max_teilnehmer": "12",
        "add_termin": "1"
    }, follow_redirects=True)

    assert response.status_code == 200
    termin = Appointment.objects(course=course, room=room, teacher=teacher, canceled=False).first()
    assert termin is not None
    assert termin.max_students == 12


def test_ft3_2b_invalid_inputs(testapp):
    teacher = User.objects.get(email="teacher@test.de")
    course1 = Course.objects.get(name="Course 0")
    course2 = Course.objects.get(name="Course 1")
    room1 = Room.objects.get(name="Room 1")
    room2 = Room.objects.get(name="Room 2")

    login_response = login_as_admin(testapp)
    assert login_response.status_code == 200

    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    response = testapp.post("/schedule_mgmt/", data={
        "datum": past_date,
        "kurs": str(course1.id),
        "raum": str(room1.id),
        "dozent": str(teacher.id),
        "max_teilnehmer": "10",
        "add_termin": "1"
    }, follow_redirects=True)

    assert response.status_code == 200
    # Prüfe auf Flash-Message im HTML
    assert "nicht in der Vergangenheit" in response.data.decode("utf-8")

    future_date = (datetime.now() + timedelta(days=5)).date()
    Appointment(
        date=future_date,
        max_students=5,
        course=course1,
        room=room1,
        teacher=teacher
    ).save()

    response = testapp.post("/schedule_mgmt/", data={
        "datum": future_date.strftime("%Y-%m-%d"),
        "kurs": str(course2.id),
        "raum": str(room2.id),
        "dozent": str(teacher.id),
        "max_teilnehmer": "8",
        "add_termin": "1"
    }, follow_redirects=True)

    assert response.status_code == 200
    text = response.data.decode("utf-8")
    # Prüfe Flash-Message bei Konflikt mit Dozent
    assert "Dozent" in text and "bereits eingeteilt" in text


def test_ft3_3a_cancel_appointment(testapp):
    teacher = User.objects.get(email="teacher@test.de")
    course = Course.objects.get(name="Course 0")
    room = Room.objects.get(name="Room 1")

    login_response = login_as_admin(testapp)
    assert login_response.status_code == 200

    future_date = datetime.now().date() + timedelta(days=3)
    termin = Appointment(
        date=future_date,
        max_students=12,
        course=course,
        room=room,
        teacher=teacher
    ).save()

    response = testapp.post("/schedule_mgmt/", data={
        "termin_id": str(termin.id),
        "cancel_termin": "1"
    }, follow_redirects=True)

    termin.reload()
    assert termin.canceled is True
    # Prüfe, dass im HTML das Wort "Gecancelt" (Status) angezeigt wird
    assert "Gecancelt" in response.data.decode("utf-8")


def test_ft3_3b_cancel_invalid(testapp):
    teacher1 = User.objects.get(email="teacher@test.de")
    teacher_role = Role.objects.get(name="Teacher")
    teacher2 = User.objects(role=teacher_role, email__ne="teacher@test.de").first()

    course1 = Course.objects.get(name="Course 0")
    course2 = Course.objects.get(name="Course 1")
    room1 = Room.objects.get(name="Room 1")
    room2 = Room.objects.get(name="Room 2")

    login_response = login_as_admin(testapp)
    assert login_response.status_code == 200

    # Alter Termin in der Vergangenheit (nicht gecancelt)
    old_termin = Appointment(
        date=datetime.now().date() - timedelta(days=5),
        max_students=5,
        course=course1,
        room=room1,
        teacher=teacher1
    ).save()

    # Seite laden und prüfen, dass für alten Termin (in Vergangenheit) kein Cancel-Button angezeigt wird
    response = testapp.get("/schedule_mgmt/", follow_redirects=True)
    page_content = response.data.decode("utf-8")
    # ❌ Button (Unicode 274c) darf nicht sichtbar sein, da Termin in Vergangenheit und somit nicht mehr stornierbar
    assert "\u274c" not in page_content

    # Termin in der Zukunft, der bereits gecancelt wurde
    future_date = datetime.now().date() + timedelta(days=3)
    canceled_termin = Appointment(
        date=future_date,
        max_students=5,
        course=course2,
        room=room2,
        teacher=teacher2,
        canceled=True
    ).save()

    # Erneuter Versuch, gecancelten Termin zu canceln - das Backend soll das "still akzeptieren" (kein Fehler),
    # aber der Status bleibt gecancelt (kein doppeltes Canceln)
    response = testapp.post("/schedule_mgmt/", data={
        "termin_id": str(canceled_termin.id),
        "cancel_termin": "1"
    }, follow_redirects=True)

    canceled_termin.reload()
    # Termin muss immer noch gecancelt sein
    assert canceled_termin.canceled is True

    # Und auf der Seite darf der Cancel-Button für den gecancelten Termin NICHT angezeigt werden
    response = testapp.get("/schedule_mgmt/", follow_redirects=True)
    page_content = response.data.decode("utf-8")
    # Kein Button zum nochmaligen Canceln
    assert "\u274c" not in page_content