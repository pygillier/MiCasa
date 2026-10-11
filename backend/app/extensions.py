"""Shared extension instances, initialised in ``create_app``."""

from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()
