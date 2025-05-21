from flask import Flask, render_template, Blueprint, session
from flask_login import login_required
from app.appointment.model import Appointment
from datetime import datetime
from bson import ObjectId

bp_bookings = Blueprint('bookings', __name__, template_folder='pages')

@bp_bookings.route('/')
@login_required
def home():
    appointments = Appointment.objects.all()

    table_data = []

    for appointment in appointments:
        if appointment.date < datetime.now().date() or appointment.students==appointment.max_students :              #Termine aus der Vergangenheit ausblenden
            continue

        new_row = {'id': str(appointment.course.id),'Kursname': f'{appointment.course.name}', 'Termin': f'{appointment.date}', 'Kursleiter' : f'{appointment.teacher.username}'
                  , 'Freie_Plaetze': f'{appointment.max_students - len(appointment.students)}', 'Raum': f'{appointment.room.name}'}
        table_data.append(new_row)


    return render_template('bookings.html', info=session, table_data=table_data)


@bp_bookings.route('/course/<string:course_id>')
@login_required
def clicked_course(course_id):
    appointment = Appointment.objects(course=ObjectId(course_id), date__gte=datetime.today()).first()


    return render_template('clicked_course.html', appointment=appointment)



