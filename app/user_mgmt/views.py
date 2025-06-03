from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from flask_login import login_required
from werkzeug.security import generate_password_hash
from app.users.models import User
from app.role.model import Role
from email_validator import validate_email, EmailNotValidError
import datetime

bp_user_mgmt = Blueprint('user_mgmt', __name__, template_folder='pages')

@bp_user_mgmt.route('/')
@login_required
def home():
    role_filter = request.args.get('role', '').strip()
    search_filter = request.args.get('search', '').strip()

    # Alle User holen
    users = User.objects.select_related()

    # Filter anwenden (in Python, nicht direkt in MongoEngine!)
    if role_filter:
        users = [u for u in users if u.role and u.role.name == role_filter]

    if search_filter:
        users = [u for u in users if search_filter.lower() in u.username.lower()]

    return render_template('show_users.html', info=session, users=users)

@bp_user_mgmt.route('/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.objects(id=user_id).first()

    if not user:
        flash("Nutzer nicht gefunden.", "danger")
        return redirect(url_for('user_mgmt.home'))

    roles = Role.objects.all()
    invalid_email = False
    weak_password = False

    if request.method == 'POST':
        new_email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()
        new_role_name = request.form.get('role', '').strip()
        new_dob = request.form.get('geburtsdatum', '').strip()

        # E-Mail validieren
        try:
            validate_email(new_email)
        except EmailNotValidError:
            invalid_email = True

        # Passwort prüfen (nur wenn eins eingegeben wurde)
        if new_password and len(new_password) < 8:
            weak_password = True

        # Fehlerbehandlung
        if not new_email or not new_role_name or not new_dob or invalid_email or weak_password:
            flash("Bitte alle Felder korrekt ausfüllen.", "danger")
            return render_template(
                'edit_user.html',
                user=user,
                roles=roles,
                info=session,
                invalid_email=invalid_email,
                weak_password=weak_password
            )

        # Prüfung auf doppelte E-Mail
        if new_email != user.username and User.objects(username=new_email).first():
            flash("Ein anderer User mit dieser E-Mail existiert bereits.", "warning")
            return render_template(
                'edit_user.html',
                user=user,
                roles=roles,
                info=session,
                invalid_email=False,
                weak_password=False
            )

        # Werte speichern
        user.email = new_email
        user.username = new_email

        if new_password:
            user.password = generate_password_hash(new_password)

        role = Role.objects(name=new_role_name).first()
        if role:
            user.role = role

        user.date_of_birth = datetime.datetime.strptime(new_dob, '%Y-%m-%d')
        user.save()

        flash("Nutzer erfolgreich aktualisiert.", "success")
        return redirect(url_for('user_mgmt.home'))

    return render_template(
        'edit_user.html',
        user=user,
        roles=roles,
        info=session,
        invalid_email=False,
        weak_password=False
    )

@bp_user_mgmt.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role_name = request.form.get('role', '').strip()
        geburtsdatum = request.form.get('geburtsdatum', '').strip()

        missing_email = not email
        missing_password = not password
        missing_role = not role_name
        missing_dob = not geburtsdatum
        invalid_email = False
        password_too_short = len(password) < 8

        try:
            validate_email(email)
        except EmailNotValidError:
            invalid_email = True

        if missing_email or missing_password or missing_role or missing_dob or invalid_email or password_too_short:
            flash("Bitte alle Pflichtfelder korrekt ausfüllen.", "danger")
            return render_template(
                'add_user.html',
                info=session,
                missing_email=missing_email,
                missing_password=missing_password,
                missing_role=missing_role,
                missing_dob=missing_dob,
                invalid_email=invalid_email,
                password_too_short=password_too_short
            )

        if User.objects(username=email).first():
            flash("Ein Benutzer mit dieser E-Mail existiert bereits.", "warning")
            return render_template(
                'add_user.html',
                info=session,
                missing_email=False,
                missing_password=False,
                missing_role=False,
                missing_dob=False,
                invalid_email=False,
                password_too_short=False
            )

        role = Role.objects(name=role_name).first()
        if not role:
            flash("Rolle nicht gefunden.", "danger")
            return render_template(
                'add_user.html',
                info=session,
                missing_email=False,
                missing_password=False,
                missing_role=False,
                missing_dob=False,
                invalid_email=False,
                password_too_short=False
            )

        new_user = User(
            username=email,
            email=email,
            password=generate_password_hash(password),
            role=role,
            date_of_birth=datetime.datetime.strptime(geburtsdatum, '%Y-%m-%d'),
            is_active=True
        )
        new_user.save()

        flash("Neuer Benutzer erfolgreich angelegt.", "success")
        return redirect(url_for('user_mgmt.home'))

    return render_template(
        'add_user.html',
        info=session,
        missing_email=False,
        missing_password=False,
        missing_role=False,
        missing_dob=False,
        invalid_email=False,
        password_too_short=False
    )

@bp_user_mgmt.route('/deactivate/<user_id>', methods=['POST'])
@login_required
def deactivate_user(user_id):
    user = User.objects(id=user_id).first()

    if not user:
        flash("Benutzer nicht gefunden.", "danger")
        return redirect(url_for('user_mgmt.home'))

    if not user.is_active:
        flash("Benutzer ist bereits deaktiviert.", "warning")
    else:
        user.is_active = False
        user.save()
        flash("Benutzer wurde deaktiviert.", "success")

    return redirect(url_for('user_mgmt.home'))

@bp_user_mgmt.route('/toggle_active/<user_id>', methods=['POST'])
@login_required
def toggle_user_active(user_id):
    user = User.objects(id=user_id).first()

    if not user:
        flash("Benutzer nicht gefunden.", "danger")
    else:
        user.is_active = not user.is_active
        user.save()
        status = "reaktiviert" if user.is_active else "deaktiviert"
        flash(f"Benutzer wurde {status}.", "success")

    return redirect(url_for('user_mgmt.edit_user', user_id=user_id))

