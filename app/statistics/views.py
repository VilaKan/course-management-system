import datetime
import calendar
import matplotlib.pyplot as plt
from flask import Blueprint, render_template, session, request
from flask_login import login_required
from collections import Counter


from app.appointment.model import Appointment

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
    date_max = datetime.date(year=int(year), month=int(month), day=31)
    appointments = Appointment.objects.filter(date__gte=date_min, date__lte=date_max)

    # Count days of the week, so we get an array with length of seven (since we have seven weekdays)
    # We just increment the counter at the correct index for each appointment
    weekday_counts = Counter()
    for appointment in appointments:
        weekday = appointment.date.weekday()  # 0 = Monday, 6 = Sunday
        weekday_counts[weekday] += 1

    # This prepares the labels (Monday, Tuesday, etc.) for the chart as well as
    labels = [calendar.day_name[i] for i in sorted(weekday_counts)]
    values = [weekday_counts[i] for i in sorted(weekday_counts)]

    # Plot pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct=generate_counts_factory(values), startangle=90)
    plt.title('Appointments by Day of the Week')
    plt.axis('equal')
    plt.tight_layout()
    #plt.show()
    plt.savefig("static/plots/appointments_pie_2025.png", dpi=300, bbox_inches='tight')
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
    year = request.form.get('yearOnly')
    return render_template('statistics.html', info=session)
