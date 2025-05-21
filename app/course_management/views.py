from flask import Blueprint, render_template, session
from flask_login import login_required

bp_course_list = Blueprint('course_list', __name__, template_folder='pages')

@bp_course_list.route('/')
@login_required
def home():
    return render_template('course_list.html', info=session)
