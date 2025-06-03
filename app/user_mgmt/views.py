import datetime
import calendar
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, session, request
from flask_login import login_required
from app.users.models import User
from collections import Counter

# define the blueprint
bp_user_mgmt = Blueprint('user_mgmt', __name__, template_folder='pages')

# index is list view
@bp_user_mgmt.route('/')
@login_required
def home():
    user_list = User.objects.all()
    return render_template('show_users.html', info=session, users=user_list)