import datetime
import calendar
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, session, request
from flask_login import login_required
from collections import Counter


from app.appointment.model import Appointment
from app.course.model import Course

# define the blueprint
bp_statistics = Blueprint('statistics', __name__, template_folder='pages')


# all routes

# index is list view
@bp_statistics.route('/')
@login_required
def home():
    return render_template('statistics.html', info=session)

# index is list view
@bp_statistics.route('/generate_year_and_month', methods=['POST'])
@login_required
def generate_year_and_month():
    year = request.form.get('yearSelect')
    month = request.form.get('monthSelect')
    date_min = datetime.date(year=int(year), month=int(month), day=1)
    last_day = calendar.monthrange(int(year), int(month))[1]
    date_max = datetime.date(int(year), int(month), last_day)
    appointments = Appointment.objects.filter(date__gte=date_min, date__lte=date_max)

    # Count days of the week, so we get an array with length of seven (since we have seven weekdays)
    # We just increment the counter at the correct index for each appointment
    weekday_counts = Counter()
    for appointment in appointments:
        weekday = appointment.date.weekday()  # 0 = Monday, 6 = Sunday
        weekday_counts[weekday] += 1

    # Manual english to german translation
    translation_days = {
        'Monday': 'Montag',
        'Tuesday': 'Dienstag',
        'Wednesday': 'Mittwoch',
        'Thursday': 'Donnerstag',
        'Friday': 'Freitag',
        'Saturday': 'Samstag',
        'Sunday': 'Sonntag'
    }

    # Manual number to month translation
    translation_months = {
        '01': 'Januar',
        '02': 'Februar',
        '03': 'März',
        '04': 'April',
        '05': 'Mai',
        '06': 'Juni',
        '07': 'Juli',
        '08': 'August',
        '09': 'September',
        '10': 'Oktober',
        '11': 'November',
        '12': 'Dezember'
    }

    # This prepares the labels (Monday, Tuesday, etc.) for the chart as well as
    labels = [calendar.day_name[i] for i in sorted(weekday_counts)]
    labels_german = [translation_days[day] for day in labels]
    values = [weekday_counts[i] for i in sorted(weekday_counts)]

    # Plot pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels_german, autopct=generate_counts_factory(values), startangle=90)
    #plt.title(f'Anzahl der Kurse pro Wochentag im {translation_months[month]} {year}')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig("static/plots/appointments_pie.png", dpi=300, bbox_inches='tight')
    return render_template('statistics.html', info=session)

# Factory function which gets called on every slice of the pie chart
# This is used to display the actual amount as an integer instead of a percentage which is the default for a matplotlib pie chart
def generate_counts_factory(values):
    def generate_counts(pct):
        total = sum(values)
        count = int(round(pct * total / 100.0))
        return f'{count}'
    return generate_counts

# index is list view
@bp_statistics.route('/generate_year_only', methods=['POST'])
@login_required
def generate_year_only():
    cmap = plt.get_cmap('tab10')
    colors = [cmap(i) for i in range(10)]
    year = request.form.get('yearOnly')
    date_min = datetime.date(year=int(year), month=1, day=1)
    last_day = calendar.monthrange(int(year), 12)[1]
    date_max = datetime.date(int(year), 12, last_day)
    appointments = Appointment.objects.filter(date__gte=date_min, date__lte=date_max)
    appointments = sorted(appointments, key=lambda appt: len(appt.students), reverse=True)
    courses = []
    students = []
    for appointment in appointments:
        course = Course.objects.get(id=appointment.course)
        courses.append(course.name)
        students.append(len(appointment.students))


    # Plot horizontal bar chart
    plt.figure(figsize=(10, 6))
    plt.barh(courses[::-1], students[::-1], color=colors)

    plt.ylabel("Kursename")
    plt.xlabel("Anzahl der Teilnehmer")
    #plt.title("Termine pro Wochentag")
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig("static/plots/appointments_bars.png", dpi=300, bbox_inches='tight')
    return render_template('statistics.html', info=session)

    return render_template('statistics.html', info=session)
