from flask import Blueprint, current_app
from datetime import datetime, time
from babel.dates import format_date, get_timezone

home = Blueprint("Home", __name__, template_folder="templates")

from . import views  # noqa: E402,F401


@home.app_context_processor
def homescreen_values():
    # What time is it ?
    dt = datetime.now(tz=get_timezone(current_app.config["TIMEZONE"]))
    if 12 < dt.hour < 17:
        greeting = "Hello"
    elif 17 <= dt.hour < 21:
        greeting = "Good evening"
    elif 21 <= dt.hour < 6:
        greeting = "Good night"
    else:
        greeting = "Good morning"

    return dict(
        greeting=greeting,
        now=format_date(
            dt,
            locale=current_app.config["LOCALE"],
            format="full",
        ),
    )
