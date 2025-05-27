from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from flask_login import login_required
from app.course.model import Course

bp_course_list = Blueprint('course_list', __name__, template_folder='pages')


# Kursliste anzeigen
@bp_course_list.route('/')
@login_required
def home():
    courses = Course.objects.order_by('name')
    return render_template('course_list.html', courses=courses, info=session)


# Kurs erstellen
@bp_course_list.route('/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name or not description:
            flash("Kursname und Beschreibung dürfen nicht leer sein.", "danger")
        elif Course.objects(name=name).first():
            flash("Ein Kurs mit diesem Namen existiert bereits.", "warning")
        else:
            Course(name=name, description=description).save()
            flash("Kurs erfolgreich angelegt.", "success")
            return redirect(url_for('course_list.home'))

    return render_template('course_create.html', info=session)


# Kurs bearbeiten
@bp_course_list.route('/edit/<course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.objects(id=course_id).first()

    if not course:
        flash("Kurs nicht gefunden.", "danger")
        return redirect(url_for('course_list.home'))

    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        new_description = request.form.get('description', '').strip()

        if not new_name or not new_description:
            flash("Kursname und Beschreibung dürfen nicht leer sein.", "danger")
        elif new_name != course.name and Course.objects(name=new_name).first():
            flash("Ein anderer Kurs mit diesem Namen existiert bereits.", "warning")
        else:
            course.name = new_name
            course.description = new_description
            course.save()
            flash("Kurs erfolgreich aktualisiert.", "success")
            return redirect(url_for('course_list.home'))

    return render_template('course_edit.html', course=course, info=session)
