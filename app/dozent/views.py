from flask import Blueprint, render_template, session
from flask_login import login_required

bp_dozent = Blueprint('dozent', __name__, template_folder='pages')

@bp_dozent.route('/termine')
@login_required
def home():
    return render_template('dozent.html', info=session)