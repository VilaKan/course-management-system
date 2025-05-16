import datetime

import click
from flask import Flask
from flask.cli import with_appcontext
from flask_assets import Environment
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_session.mongodb import MongoDBSessionInterface
from mongoengine.connection import get_db

from webassets.loaders import PythonLoader as PythonAssetsLoader
from werkzeug.security import generate_password_hash

from app import assets
from app.appointment.model import Appointment
from app.course.model import Course
from app.users.models import User
from app.role.model import Role
from app.room.model import Room

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
    db = MongoEngine()
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

    # register blueprints
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_users, url_prefix='/users')
    app.register_blueprint(bp_books, url_prefix='/books')
    app.register_blueprint(bp_statistics, url_prefix='/statistics')





@click.command('init-db')
@with_appcontext
def init_db_command():
    create_users()
    create_roles()
    create_appointments()
    create_courses()
    create_rooms()

def create_rooms():
    for i in range(0, 20):
        room = Room(
            id=i,
            name=f"Room {i}",
        )
        room.save()
        click.echo(f'Created Room{i}')

def create_courses():
    for i in range(0, 20):
        course = Course(
            id=i,
            name=f"Course {i}",
            description=f"Course {i} description"
        )
        course.save()
        click.echo(f'Created course {i}')

def create_appointments():
    ## Create Appointment
    appointment_one = Appointment(id=0, date=datetime.datetime(2025, 1, 1), max_students=12, course=0,room=0,teacher=1, students=[0,1,2,3,4,5,6,7,8,9])
    appointment_two = Appointment(id=1, date=datetime.datetime(2025, 1, 2), max_students=12, course=1,room=0,teacher=1, students=[0,1,2,3,4,5,6,7,8])
    appointment_three = Appointment(id=2, date=datetime.datetime(2025, 1, 3), max_students=12, course=2,room=0,teacher=1, students=[0,1,2,3,4,5,6,7])
    appointment_four = Appointment(id=3, date=datetime.datetime(2025, 1, 4), max_students=12, course=3,room=0,teacher=1, students=[0,1,2,3,4,5,6])
    appointment_five = Appointment(id=4, date=datetime.datetime(2025, 1, 5), max_students=12, course=4,room=0,teacher=1, students=[0,1,2,3,4,5])
    appointment_six = Appointment(id=5, date=datetime.datetime(2025, 1, 6), max_students=12, course=5,room=0,teacher=1, students=[0,1,2,3,4])
    appointment_seven = Appointment(id=6, date=datetime.datetime(2025, 1, 7), max_students=12, course=6,room=0,teacher=1, students=[0,1,2,3])
    appointment_eight = Appointment(id=7, date=datetime.datetime(2025, 1, 8), max_students=12, course=7,room=0,teacher=1, students=[0,1,2])
    appointment_nine = Appointment(id=8, date=datetime.datetime(2025, 1, 9), max_students=12, course=8,room=0,teacher=1, students=[0,1])
    appointment_ten = Appointment(id=9, date=datetime.datetime(2025, 1, 10), max_students=12, course=9,room=0,teacher=1, students=[0])
    appointment_one.save()
    appointment_two.save()
    appointment_three.save()
    appointment_four.save()
    appointment_five.save()
    appointment_six.save()
    appointment_seven.save()
    appointment_eight.save()
    appointment_nine.save()
    appointment_ten.save()
    click.echo('Created Appointments')

def create_roles():
    ## Create Roles
    role_admin = Role(id=0, name="Admin")
    role_teacher = Role(id=1, name="Teacher")
    role_user = Role(id=2, name="User")

    role_admin.save()
    role_teacher.save()
    role_user.save()
    click.echo('Created Roles "Admin" and "Teacher" and "User"')

def create_users():
    ## Create an Admin
    admin_email = "admin@test.de"
    admin = User(id=0, username=admin_email, password=generate_password_hash("test"), email=admin_email, role=0, date_of_birth=datetime.datetime(1995, 1, 31))
    admin.save()
    click.echo('Admin user with username testmail@test.de and password test created')

    ## Create a Teacher
    teacher_email = "teacher@test.de"
    teacher = User(id=1, username=teacher_email, password=generate_password_hash("test"), email=teacher_email, role=1,
                   date_of_birth=datetime.datetime(1995, 1, 31))
    teacher.save()
    click.echo('Teacher user with username teacher@test.de and password test created')

    for i in range(0, 11):
        email = f"student{i}@test.de"
        student = User(
            id=i,
            username=email,
            password=generate_password_hash("test"),
            email=email,
            role=2,
            date_of_birth=datetime.datetime(1995, 1, 31)
        )
        student.save()
        click.echo(f'Student user with username {email} and password test created')