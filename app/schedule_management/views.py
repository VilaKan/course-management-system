from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.appointment.model import Appointment
from app.room.model import Room
from app.users.models import User
from app.course.model import Course
from app.role.model import Role

bp_schedulemanagement = Blueprint('schedulemanagement', __name__, template_folder='pages')

@bp_schedulemanagement.route("/Terminverwaltung", methods=["GET", "POST"])
@login_required
def schedule_management():
    if current_user.role.name != "Admin":
        abort(403)

    if request.method == "POST":
        if 'add_termin' in request.form:
            datum_str = request.form.get('datum')
            kurs_id = request.form.get('kurs')
            raum_id = request.form.get('raum')
            dozent_id = request.form.get('dozent')
            max_teilnehmer = int(request.form.get('max_teilnehmer'))

            datum = datetime.strptime(datum_str, "%Y-%m-%d").date()

            # Prüfen: kein Datum in der Vergangenheit
            if datum < datetime.now().date():
                error = "Ein Termin kann nicht in der Vergangenheit liegen."
            else:
                kurs = Course.objects(id=kurs_id).first()
                raum = Room.objects(id=raum_id).first()
                dozent = User.objects(id=dozent_id).first()

                # Prüfen: gleicher Kurs/Raum/Tag
                konflikt_kurs_raum = Appointment.objects(
                    date=datum,
                    room=raum,
                    course=kurs,
                    canceled=False
                ).first()

                # Prüfen: Dozent bereits an dem Tag gebucht
                konflikt_dozent = Appointment.objects(
                    date=datum,
                    teacher=dozent,
                    canceled=False
                ).first()

                # Prüfen: Duplikat vermeiden (gleicher Kurs, Raum, Dozent, Tag)
                doppelter_termin = Appointment.objects(
                    date=datum,
                    room=raum,
                    course=kurs,
                    teacher=dozent,
                    canceled=False
                ).first()

                if konflikt_kurs_raum:
                    flash(f"An diesem Tag findet bereits ein Kurs im Raum {raum.name} statt.", "danger")
                elif konflikt_dozent:
                    flash(f"Dozent {dozent.email} ist an diesem Tag bereits eingeteilt.", "danger")
                elif doppelter_termin:
                    flash("Ein identischer Termin existiert bereits.", "danger")
                else:
                    # Termin speichern
                    Appointment(
                        date=datum,
                        max_students=max_teilnehmer,
                        course=kurs,
                        room=raum,
                        teacher=dozent,
                        students=[],
                        canceled=False
                    ).save()

        elif 'cancel_termin' in request.form:
            termin_id = request.form.get('termin_id')
            termin = Appointment.objects(id=termin_id).first()
            if termin:
                termin.canceled = True
                termin.save()

        return redirect(url_for('schedulemanagement.schedule_management'))

    termine = Appointment.objects().order_by('date')
    courses = Course.objects()
    rooms = Room.objects()
    teacher_role = Role.objects(name="Teacher").first()
    teachers = User.objects(role=teacher_role)

    now = datetime.now().date()

    return render_template(
        'schedule_management.html',
        termine=termine,
        courses=courses,
        rooms=rooms,
        teachers=teachers,
        now=now,
        info=None,
    )
