from flask import Flask, render_template, Blueprint, session
from flask_login import login_required
from flask_mongoengine import MongoEngine
from app.appointment.model import Appointment

bp_bookings = Blueprint('bookings', __name__, template_folder='pages')

@bp_bookings.route('/')
@login_required
def home():
    appointments = Appointment.objects.all()

    table_data = []

    for appointment in appointments:

        new_row = {'Kursname': f'{appointment.course.name}', 'Termin': f'{appointment.date}', 'Kursleiter' : f'{appointment.teacher.username}'
                  , 'Freie_Plaetze': f'{appointment.max_students - len(appointment.students)}', 'Raum': f'{appointment.room.name}'}
        table_data.append(new_row)


    return render_template('bookings.html', info=session, table_data=table_data)


