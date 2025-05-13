from flask import Blueprint, render_template, session
from flask_login import login_required

# define the blueprint
bp_statistics = Blueprint('statistics', __name__, template_folder='pages')


# all routes

# index is list view
@bp_statistics.route('/')
@login_required
def home():
    return render_template('statistics.html', info=session)
