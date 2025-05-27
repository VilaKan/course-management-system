from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from app.appointment.model import Appointment
from app.course.model import Course
from app.room.model import Room

bp_dozent = Blueprint('dozent', __name__, template_folder='pages')

@bp_dozent.route('/')
@login_required
def home():
    # Get all appointments for the logged-in teacher
    appointments = Appointment.objects(teacher=current_user.id)

    # Prepare list with course name, room name, student count, and date
    terminliste = []
    for appt in appointments:
        kurs = appt.course
        raum = appt.room
        teilnehmer = len(appt.students)
        terminliste.append({
            'date': appt.date.strftime('%d. %b %Y'),
            'kurs': kurs.name,
            'raum': raum.name,
            'anzahl': teilnehmer
        })

    return render_template('dozent.html', termine=terminliste, info=session)
