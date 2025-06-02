from flask import Blueprint, render_template, session, request
from flask_login import login_required, current_user
from app.appointment.model import Appointment
from app.course.model import Course
from app.room.model import Room
from app.users.models import User
import datetime

bp_dozent = Blueprint('dozent', __name__, template_folder='pages')

@bp_dozent.route('/', methods=['GET', 'POST'])
@login_required
def home():
    all_appointments = Appointment.objects(teacher=current_user.id)
    appointments = all_appointments

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    filter_applied = False

    if start_date and end_date:
        try:
            date_start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            date_end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            appointments = all_appointments.filter(date__gte=date_start, date__lte=date_end)
            filter_applied = True
        except ValueError:
            pass

    terminliste = []
    for appt in appointments:
        kurs = appt.course
        raum = appt.room
        teilnehmer = len(appt.students)

        terminliste.append({
            'id': str(appt.id),
            'date': appt.date.strftime('%d. %b %Y'),
            'kurs': kurs.name,
            'raum': raum.name,
            'anzahl': teilnehmer
        })

    error_message = None
    if not terminliste:
        if filter_applied and all_appointments:
            error_message = "Keine Termine im gewählten Zeitraum gefunden."
        elif not all_appointments:
            error_message = "Keine Termine gefunden."

    return render_template('dozent.html', termine=terminliste, info=session, error_message=error_message)

@bp_dozent.route('/teilnehmerliste', methods=['POST'])
@login_required
def teilnehmerliste():
    appointment_id = request.form.get('appointment_id')
    appointment = Appointment.objects.get(id=appointment_id)

    students = User.objects(id__in=[student.id for student in appointment.students])

    return render_template('teilnehmerliste.html', students=students, info=session)
