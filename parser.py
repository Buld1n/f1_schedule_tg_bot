import datetime
from ics import Calendar
import pytz


def load_calendar():
    with open('f1-calendar_gp.ics', 'r') as file:
        return Calendar(file.read())


def get_next_race():
    calendar = load_calendar()
    now = datetime.datetime.now(pytz.utc)

    next_race = None
    for event in calendar.events:
        if event.begin > now:
            if not next_race or event.begin < next_race['start']:
                next_race = {'summary': event.summary, 'start': event.begin}

    return next_race


def is_race_in_5_minutes(race):
    now = datetime.datetime.now(pytz.utc)
    time_difference = race['start'] - now
    return 0 < time_difference.total_seconds() <= 300

