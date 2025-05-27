from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from flask_login import login_required
from app.course.model import Course

bp_course_list = Blueprint('course_list', __name__, template_folder='pages')


@bp_course_list.route('/')
@login_required
def home():
    courses = Course.objects.order_by('name')
    return render_template('course_list.html', courses=courses, info=session)


@bp_course_list.route('/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        # Validierungen
        if not name or not description:
            flash("Kursname und Beschreibung dürfen nicht leer sein.", "danger")
        elif Course.objects(name=name).first():
            flash("Ein Kurs mit diesem Namen existiert bereits.", "warning")
        else:
            Course(name=name, description=description).save()
            flash("Kurs erfolgreich angelegt.", "success")
            return redirect(url_for('course_list.home'))

    return render_template('course_create.html', info=session)
