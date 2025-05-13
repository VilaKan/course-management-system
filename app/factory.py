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
    room_one = Room(id=0, name="Coding Lab")
    room_one.save()

    room_two = Room(id=1, name="Cooking Lab")
    room_two.save()

    click.echo('Created 2 courses')

def create_courses():
    course_one = Course(id=0, name="Programming for Beginners", description="A beginner course for everyone to learn coding!")
    course_one.save()

    course_two = Course(id=1, name="Cooking for Beginners", description="A beginner course for everyone to learn cooking!")
    course_two.save()

    click.echo('Created 2 courses')

def create_appointments():
    ## Create Appointment
    appointment = Appointment(id=0, date=datetime.datetime(1995, 1, 31), max_students=12, course=0,room=0,teacher=1, students=[2,3])
    appointment.save()
    click.echo('Created Appointment')


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
    admin = User(id=0, username=admin_email, password=generate_password_hash("test"), email=admin_email, role=0,
                 date_of_birth=datetime.datetime(1995, 1, 31))
    admin.save()
    click.echo('Admin user with username testmail@test.de and password test created')

    ## Create a Teacher
    teacher_email = "teacher@test.de"
    teacher = User(id=1, username=teacher_email, password=generate_password_hash("test"), email=teacher_email, role=1,
                   date_of_birth=datetime.datetime(1995, 1, 31))
    teacher.save()
    click.echo('Teacher user with username teacher@test.de and password test created')

    ## Create an Student
    student_one_email = "student_one@test.de"
    student_one = User(id=2, username=student_one_email, password=generate_password_hash("test"), email=student_one_email, role=2,
                       date_of_birth=datetime.datetime(1995, 1, 31))
    student_one.save()
    click.echo('Student user with username student_one@test.de and password test created')

    ## Create an Student
    student_two_email = "student_two@test.de"
    student_two = User(id=3, username=student_two_email, password=generate_password_hash("test"), email=student_two_email, role=2,
                       date_of_birth=datetime.datetime(2025, 1, 31))
    student_two.save()
    click.echo('Student user with username student_two@test.de and password test created')