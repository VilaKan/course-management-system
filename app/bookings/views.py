from flask import Flask, render_template, Blueprint, session, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.appointment.model import Appointment
from datetime import datetime
from bson import ObjectId
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from textwrap import wrap







bp_bookings = Blueprint('bookings', __name__, template_folder='pages')

#Terminübersichtstabelle mit allen Terminen die vom Kursleiter/Admin erstellt wurden
#Wenn das heutige Datum weiter ist als das vom Termin wird es ausgeblendet
#Wenn die Maximale Anzahl der Plätze erreicht wurde dann ausblenden
#Wenn der Current User schon den Kurs belegt hat, dann ausblenden
@bp_bookings.route('/')
@login_required
def home():
    appointments = Appointment.objects.all()

    table_data = []

    for appointment in appointments:
        if appointment.date < datetime.now().date() :
            continue

        if len(appointment.students)==appointment.max_students :              #Termine aus der Vergangenheit ausblenden
            continue

        if current_user in appointment.students :
            continue


        new_row = {'id': str(appointment.course.id),
                   'Kursname': f'{appointment.course.name}',
                   'Termin': f'{appointment.date}',
                   'Kursleiter' : f'{appointment.teacher.username}'
                  ,'Freie_Plaetze': f'{appointment.max_students - len(appointment.students)}',
                   'Max_studenten': f'{appointment.max_students}',
                   'Raum': f'{appointment.room.name}',}
        table_data.append(new_row)
    return render_template('bookings.html', info=session, table_data=table_data)




#Benutzer sieht die Terminübersicht und wählt ein Termin seiner Wahl aus und wird weitergeleitet zu den
# Inforrmationen und zu einem Button mit "Kurs belegen"
@bp_bookings.route('/course/<string:course_id>')
@login_required
def clicked_course(course_id):
    appointment = Appointment.objects(course=ObjectId(course_id), date__gte=datetime.now()).first()

    if not appointment:
        return redirect(url_for('bookings.home'))
    return render_template('clicked_course.html', appointment=appointment, appointment_id=appointment.id)





#Kursbelegungen mit Filterung : Wenn der selber Kursleiter im selben Datum belegt wird,dann Warnmeldung
#Wenn Kurs noch einen freien Platz hatte , aber einer der Benutzer schneller als der andere war Warnmeldung
@bp_bookings.route('/booked_course/<string:appointment_id>', methods=['POST'])
def booked_course(appointment_id):
    appointment = Appointment.objects(id=ObjectId(appointment_id)).first()
    exestiert_bereits = Appointment.objects(date=appointment.date, teacher=appointment.teacher,students=current_user, id__ne=appointment.id).first()

    if len(appointment.students) == appointment.max_students:
        flash("Der Kurs wurde soeben von einem anderen Nutzer belegt worden", 'danger')
        return redirect(url_for('bookings.home'))


    #selben Lehrer am selben Termindatum nicht möglich
    if exestiert_bereits:
        flash("Warnung : Selben Kursleiter am selben Termindatum nicht möglich", 'danger')
        return redirect(url_for('bookings.home'))

    appointment.students.append(current_user)
    appointment.save()
    flash("Kurs wurde erfolgreich belegt", 'success')
    return redirect(url_for('bookings.home'))


#Meine Kurser Terminliste aller Belegungen des Benutzers
@bp_bookings.route('/my_courses')
@login_required
def my_courses():
    my_courses = Appointment.objects(students=current_user)

    table_data = []

    for kurse in my_courses :

        if current_user not in kurse.students :
            continue


        new_row = { 'id': str(kurse.id),
                    'Kursname': f'{kurse.course.name}',
                    'Termin': f'{kurse.date}',
                    'Kursleiter': f'{kurse.teacher.username}',
                    'Raum': f'{kurse.room.name}',
                    'Studenten': f'{kurse.students}'}
        table_data.append(new_row)


    return render_template('my_courses.html', info=session, my_courses=table_data)



@bp_bookings.route('/my_clicked_courses/<string:appointment_id>')
@login_required
def my_clicked_courses(appointment_id):

    appointment = Appointment.objects(id=ObjectId(appointment_id)).first()
    return render_template('my_clicked_courses.html',info=session,appointment=appointment,
    appointment_id=appointment.id)




@bp_bookings.route('/logout_courses/<string:appointment_id>',methods=['POST'])
@login_required
def logout_courses(appointment_id):
    kurse = Appointment.objects(id=ObjectId(appointment_id)).first()

    if current_user not in kurse.students :
        return redirect(url_for('bookings.my_courses'))

    if kurse.date <= datetime.now().date():
        flash("Warnung: Abmeldung am Kurstag nicht mehr möglich", 'danger')
        return redirect(url_for('bookings.my_courses'))

    kurse.students.remove(current_user)
    kurse.save()
    flash("Kurs wurde erfolgreich abgemeldet", 'success')
    return redirect(url_for('bookings.my_courses'))



@bp_bookings.route('/confirmed_participant_pdf/<string:appointment_id>')
@login_required
def confirmed_participant_pdf(appointment_id):
    appointments = Appointment.objects(id=ObjectId(appointment_id)).first()

    buffer= BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y=height-60

    #text
    p.setFont("Helvetica-Bold", 15)
    p.drawString(50,y, f"Dies ist eine offizielle Bestätigung, dass {current_user.username} am {appointments.date} erfolgreich am Kurs {appointments.course.name} teilgenommen hat. Der Kurs wurde von {appointments.teacher.username} geleitet und fand im Raum {appointments.room.name} statt")

    p.showPage()
    p.save()

    buffer.seek(0)
    return send_file(buffer,mimetype='application/pdf', download_name='teilnahmebestätigung.pdf',as_attachment=True)











