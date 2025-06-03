import datetime

import click
from flask import Flask
from flask.cli import with_appcontext
from flask_assets import Environment
from app.database import db
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_session.mongodb import MongoDBSessionInterface
from mongoengine.connection import get_db

from webassets.loaders import PythonLoader as PythonAssetsLoader
from werkzeug.security import generate_password_hash

from app import assets
from app.course.model import Course
from app.role.model import Role
from app.users.models import User
from app.room.model import Room
from app.appointment.model import Appointment

assets_env = Environment()



def create_app(config=None):
    """
    Factory pattern; create new app with specified config
    :param config: configuration object
    :return: app object
    """

    # new app object
    app = Flask('flask-example')

    # configure app
    app.config.from_object(config)

    # set up database
    db.init_app(app)

    # use mongo engine for session store
    client = get_db().client
    app.session_interface = MongoDBSessionInterface(app,client=client,permanent=False)

    # set up assets
    assets_env.init_app(app)

    # setup init command
    app.cli.add_command(init_db_command)

    # set up toolbar
    debug_toolbar = DebugToolbarExtension()
    debug_toolbar.init_app(app)

    # initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.objects.get(pk=user_id)

    # import and register the different asset bundles
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)

    # load blueprints
    load_blueprints(app)

    return app


def load_blueprints(app):
    """
    Load all blueprints
    :param app: app in which blueprints are registered
    :return:
    """

    from app.users.views import bp_users
    from app.main.views import bp_main
    from app.books.views import bp_books
    from app.statistics.views import bp_statistics
    from app.dozent.views import bp_dozent
    from app.user_mgmt.views import bp_user_mgmt

    # register blueprints
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_users, url_prefix='/users')
    app.register_blueprint(bp_books, url_prefix='/books')
    app.register_blueprint(bp_statistics, url_prefix='/statistics')
    app.register_blueprint(bp_dozent, url_prefix='/dozent')
    app.register_blueprint(bp_user_mgmt, url_prefix='/user_mgmt')





@click.command('init-db')
@with_appcontext
def init_db_command():
    create_rooms()
    create_roles()
    create_users()
    create_courses()
    create_appointments()

def create_rooms():
    for i in range(0, 20):
        room = Room(
            name=f"Room {i}",
        )
        room.save()
        click.echo(f'Created Room{i}')

def create_courses():
    for i in range(0, 20):
        course = Course(
            name=f"Course {i}",
            description=f"Course {i} description"
        )
        course.save()
        click.echo(f'Created course {i}')


def create_appointments():
    rooms = Room.objects.all()
    courses = Course.objects.all()
    teacher_role = Role.objects.filter(name="Teacher").first()
    user_role = Role.objects.filter(name="User").first()
    teacher = User.objects.filter(role=teacher_role).first()
    users = User.objects.filter(role=user_role)

    for i in range(10):
        appointment = Appointment(date=datetime.datetime(2025, 1, i+1), max_students=12, course=courses[i], room=rooms[i], teacher=teacher, students=users[0:i+1])
        appointment.save()

    click.echo('Created Appointments')

def create_roles():
    ## Create Roles
    role_admin = Role(name="Admin")
    role_teacher = Role(name="Teacher")
    role_user = Role(name="User")

    role_admin.save()
    role_teacher.save()
    role_user.save()
    click.echo('Created Roles "Admin" and "Teacher" and "User"')

def create_users():
    admin_role = Role.objects.filter(name="Admin").first()
    teacher_role = Role.objects.filter(name="Teacher").first()
    user_role = Role.objects.filter(name="User").first()
    ## Create an Admin
    admin_email = "admin@test.de"
    admin = User(username=admin_email, password=generate_password_hash("test"), email=admin_email, role=admin_role, date_of_birth=datetime.datetime(1995, 1, 31), is_active= True)
    admin.save()
    click.echo('Admin user with username admin@test.de and password test created')

    ## Create a Teacher
    teacher_email = "teacher@test.de"
    teacher = User(username=teacher_email, password=generate_password_hash("test"), email=teacher_email, role=teacher_role,
                   date_of_birth=datetime.datetime(1995, 1, 31), is_active= True)
    teacher.save()
    click.echo('Teacher user with username teacher@test.de and password test created')

    for i in range(0, 11):
        email = f"student{i}@test.de"
        student = User(
            username=email,
            password=generate_password_hash("test"),
            email=email,
            role=user_role,
            date_of_birth=datetime.datetime(1995, 1, 31),
            is_active=True
        )
        student.save()
        click.echo(f'Student user with username {email} and password test created')