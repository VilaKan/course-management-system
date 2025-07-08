from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from flask_login import login_required
from app.course.model import Course

# Blueprint für Kurslisten-Funktionalität
bp_course_list = Blueprint('course_list', __name__, template_folder='pages')

# Kursübersicht anzeigen (Startseite)
@bp_course_list.route('/')
@login_required  # Nur eingeloggte Nutzer dürfen die Seite sehen
def home():
    # Kurse alphabetisch nach Name sortieren
    courses = Course.objects.order_by('name')
    return render_template('course_list.html', courses=courses, info=session)

# Neuen Kurs erstellen
@bp_course_list.route('/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'POST':
        # Eingaben aus dem Formular holen und Leerzeichen abschneiden
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        # Validierung: Felder dürfen nicht leer sein
        if not name or not description:
            flash("Kursname und Beschreibung dürfen nicht leer sein.", "danger")

        # Validierung: Kursname muss eindeutig sein
        elif Course.objects(name=name).first():
            flash("Ein Kurs mit diesem Namen existiert bereits.", "warning")

        # Kurs ist gültig – speichern und zur Kursliste zurück
        else:
            Course(name=name, description=description).save()
            flash("Kurs erfolgreich angelegt.", "success")
            return redirect(url_for('course_list.home'))

    # Wenn GET oder Fehler: Erstellungsformular anzeigen
    return render_template('course_create.html', info=session)

# Bestehenden Kurs bearbeiten
@bp_course_list.route('/edit/<course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    # Kurs anhand der ID aus der Datenbank holen
    course = Course.objects(id=course_id).first()

    # Falls der Kurs nicht existiert, zurück zur Kursliste
    if not course:
        flash("Kurs nicht gefunden.", "danger")
        return redirect(url_for('course_list.home'))

    if request.method == 'POST':
        # Neue Werte aus dem Formular holen
        new_name = request.form.get('name', '').strip()
        new_description = request.form.get('description', '').strip()

        # Validierung: Felder dürfen nicht leer sein
        if not new_name or not new_description:
            flash("Kursname und Beschreibung dürfen nicht leer sein.", "danger")

        # Wenn der neue Name anders ist, prüfen ob es den schon gibt
        elif new_name != course.name and Course.objects(name=new_name).first():
            flash("Ein anderer Kurs mit diesem Namen existiert bereits.", "warning")

        # Alles passt – Kursdaten speichern
        else:
            course.name = new_name
            course.description = new_description
            course.save()
            flash("Kurs erfolgreich aktualisiert.", "success")
            return redirect(url_for('course_list.home'))

    # Wenn GET oder Fehler: Bearbeitungsformular anzeigen
    return render_template('course_edit.html', course=course, info=session)
