from flask import Flask, render_template, Blueprint, session
from flask_login import login_required
from flask_mongoengine import MongoEngine
from app.appointment.model import Appointment

bp_bookings = Blueprint('bookings', __name__, template_folder='pages')

@bp_bookings.route('/')
@login_required
def home():
    appointments = Appointment.objects.all()

    for appointment in appointments:
        free_spots = appointment.max_students - len(appointment.students)

    return render_template('bookings.html', info=session)
