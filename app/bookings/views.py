from flask import Flask, render_template, Blueprint, session, redirect, url_for, flash, send_file
from flask_login import login_required, current_user

from app import appointment
from app.appointment.model import Appointment
from datetime import datetime
from bson import ObjectId
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from textwrap import wrap




bp_bookings = Blueprint('bookings', __name__, template_folder='pages')

#appointment-table with all appointments from courseleader/Admin created
# If today's date is later than the course date → hide the course
# If the maximum number of participants has been reached → hide the course
# If the current user has already registered for the course → hide the course

@bp_bookings.route('/')
@login_required
def home():
    appointments = Appointment.objects.all()

    table_data = []

    for appointment in appointments:
        if appointment.date < datetime.now().date() :
            continue

        if current_user in appointment.students :
            continue

        new_row = {'id': str(appointment.course.id),
                   'Kursname': f'{appointment.course.name}',
                   'Termin': f"{appointment.date.strftime('%d.%m.%Y')}",
                   'Kursleiter' : f'{appointment.teacher.username}'
                  ,'Freie_Plaetze': f'{appointment.max_students - len(appointment.students)}',
                   'Max_studenten': f'{appointment.max_students}',
                   'Raum': f'{appointment.room.name}',
                   'Storniert' : f'{appointment.canceled}'}
        table_data.append(new_row)
    return render_template('bookings.html', info=session, table_data=table_data)




# Benutzer sieht die Terminübersicht und wählt ein Termin seiner Wahl aus und wird weitergeleitet zu den
# Inforrmationen und zu einem Button mit "Kurs belegen"
@bp_bookings.route('/course/<string:course_id>')
@login_required
def clicked_course(course_id):
    appointment = Appointment.objects(course=ObjectId(course_id)).first()


    return render_template('clicked_course.html', appointment=appointment, appointment_id=appointment.id, info=session)





#if course is full, flash warnsignal
#course can only be taken once a day , if you want to book more than 1 course in the same day, flash warnsignal
#if course has been succesfully booked
#if appointment is canceled flash warnsignal
@bp_bookings.route('/booked_course/<string:appointment_id>', methods=['POST'])
def booked_course(appointment_id):
    appointment = Appointment.objects(id=ObjectId(appointment_id)).first()


    if len(appointment.students) == appointment.max_students:
        flash("Der Kurs ist voll", 'danger')
        return redirect(url_for('bookings.home'))

    samedate = Appointment.objects(date=appointment.date, students= current_user).first()
    if samedate:
        flash("Du hast bereits einen Termin am selben Tag belegt",'danger')
        return redirect(url_for('bookings.home'))

    appointment_canceled = Appointment.objects(canceled=appointment.canceled == True).first()

    if appointment.canceled:
        flash("Der Termin findet nicht mehr statt", 'danger')
        return redirect(url_for('bookings.home'))


    appointment.students.append(current_user)
    appointment.save()
    flash("Kurs wurde erfolgreich belegt", 'success')
    return redirect(url_for('bookings.home'))


#my courses: appointment-lists of all bookings of the user
@bp_bookings.route('/my_courses')
@login_required
def my_courses():
    my_courses = Appointment.objects(students=current_user)

    table_data = []

    for appointment in my_courses :

        if current_user not in appointment.students :
            continue


        new_row = { 'id': str(appointment.id),
                    'Kursname': f'{appointment.course.name}',
                    'Termin': f'{appointment.date}',
                    'Kursleiter': f'{appointment.teacher.username}',
                    'Raum': f'{appointment.room.name}',
                    'Studenten': f'{appointment.students}',
                    'Storniert': f'{appointment.canceled}'}
        table_data.append(new_row)


    return render_template('my_courses.html', info=session, my_courses=table_data)


#tables of my courses that user applied to
@bp_bookings.route('/my_clicked_courses/<string:appointment_id>')
@login_required
def my_clicked_courses(appointment_id):

    appointment = Appointment.objects(id=ObjectId(appointment_id)).first()
    return render_template('my_clicked_courses.html',info=session,appointment=appointment,
    appointment_id=appointment.id)



#logout of courses if the coursedate is still in the future
@bp_bookings.route('/logout_courses/<string:appointment_id>',methods=['POST'])
@login_required
def logout_courses(appointment_id):
    kurse = Appointment.objects(id=ObjectId(appointment_id)).first()

    if current_user not in kurse.students :
        return redirect(url_for('bookings.my_courses'))

    if kurse.date < datetime.now().date():
        flash("Warnung: Abmeldung am Kurstag oder nach Kurstag nicht mehr möglich", 'danger')
        return redirect(url_for('bookings.my_courses'))

    kurse.students.remove(current_user)
    kurse.save()
    flash("Kurs wurde erfolgreich abgemeldet", 'success')
    return redirect(url_for('bookings.my_courses'))


#pdf to confirm the participation of the course after course took place
# if course didnt took place yet, flash warnsignal

@bp_bookings.route('/confirmed_participant_pdf/<string:appointment_id>')
@login_required
def confirmed_participant_pdf(appointment_id):
    appointments = Appointment.objects(id=ObjectId(appointment_id)).first()

    if appointments.date > datetime.now().date():
        flash("Teilnahmenachweis erst nach Kurstermin möglich, bitte versuche es erneut sobald der Kurs abgeschlossen ist",'danger')
        return redirect(url_for('bookings.my_clicked_courses', appointment_id=appointments.id))

    appointment_canceled = Appointment.objects(canceled=appointments.canceled == True).first()

    if appointment_canceled:
        flash("Der Termin wurde storniert, Teilnahmenachweis nicht möglich ", 'danger')
        return redirect(url_for('bookings.my_clicked_courses', appointment_id=appointments.id))


    buffer= BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y= height- 60


    #text
    text= f"Dies ist eine offizielle Bestätigung, dass {current_user.username} am {appointments.date} erfolgreich am Kurs {appointments.course.name} teilgenommen hat. Der Kurs wurde von {appointments.teacher.username} geleitet und fand im Raum {appointments.room.name} statt"
    p.setFont("Helvetica-Bold", 15)
    wrapped_lines= wrap(text,width=70)

    for line in wrapped_lines:
        p.drawString(50, y, line)
        y -= 25

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer,mimetype='application/pdf', download_name='teilnahmebestätigung.pdf',as_attachment=True)












