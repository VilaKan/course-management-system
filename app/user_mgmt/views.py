from app.users.models import User
from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from flask_login import login_required
from werkzeug.security import generate_password_hash

# define the blueprint
bp_user_mgmt = Blueprint('user_mgmt', __name__, template_folder='pages')

# index is list view
@bp_user_mgmt.route('/')
@login_required
def home():
    user_list = User.objects.all()
    return render_template('show_users.html', info=session, users=user_list)

@bp_user_mgmt.route('/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.objects(id=user_id).first()

    if not user:
        flash("Kurs nicht gefunden.", "danger")
        return redirect(url_for('user_mgmt.home'))

    if request.method == 'POST':
        new_name = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()

        if not new_name or not new_password:
            flash("E-Mail und Passwort dürfen nicht leer sein.", "danger")
        elif new_name != user.username and User.objects(name=new_name).first():
            flash("Ein anderer User mit dieser E-Mail existiert bereits.", "warning")
        else:
            user.email = new_name
            user.username = new_name
            user.password = generate_password_hash(new_password)
            user.save()
            flash("Nutzer erfolgreich aktualisiert.", "success")
            return redirect(url_for('user_mgmt.home'))

    return render_template('edit_user.html', user=user, info=session)
