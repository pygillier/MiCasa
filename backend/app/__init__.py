"""MiCasa Flask application factory."""

import os

from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .config import Config
from .extensions import db, migrate, scheduler
from .logs import setup_logging


@event.listens_for(Engine, "connect")
def _sqlite_pragmas(dbapi_conn, _):
    """Enable foreign keys and WAL on every new SQLite connection."""
    if dbapi_conn.__class__.__module__.startswith("sqlite3"):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA journal_mode=WAL")
        cur.close()


def create_app(config_object=Config) -> Flask:
    """Build the app: logging, DB, auth, blueprints and (if enabled) the job scheduler."""
    app = Flask(__name__)
    app.config.from_object(config_object)
    setup_logging(app.config["LOG_LEVEL"], app.config["LOG_JSON"])
    app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 14

    db.init_app(app)
    migrate.init_app(app, db)

    from . import auth, models  # noqa: F401
    from .blueprints import register_blueprints
    from .features import jobs

    auth.init_oauth(app)
    register_blueprints(app)

    # Under the Werkzeug reloader the app is also created in the watcher parent
    # process; only the serving child (WERKZEUG_RUN_MAIN) may run the scheduler.
    reloader_parent = app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true"
    if app.config["SCHEDULER_ENABLED"] and not reloader_parent:
        from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

        app.config["SCHEDULER_JOBSTORES"] = {
            "default": SQLAlchemyJobStore(url=app.config["SQLALCHEMY_DATABASE_URI"])
        }
        scheduler.init_app(app)
        jobs.register(app)
        scheduler.start()
    else:
        jobs.register(app)
    return app
