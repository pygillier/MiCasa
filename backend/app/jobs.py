"""Scheduled jobs. Referenced by textual path so the SQLAlchemy job store can persist them."""

from datetime import UTC, datetime, timedelta
from functools import wraps

from loguru import logger

from . import kuma, settings, weather
from .extensions import db, scheduler
from .models import JobRun, WeatherCache, utcnow

KEEP_RUNS = 10
_app = None


def tracked(job_id: str):
    """Run inside the app context and record a JobRun, keeping the 10 most recent per job."""

    def deco(fn):
        @wraps(fn)
        def wrapper():
            with _app.app_context():
                started, status, message = utcnow(), "ok", ""
                try:
                    message = str(fn() or "")
                except Exception as exc:  # noqa: BLE001 - recorded; the scheduler must survive
                    logger.exception("job {} failed", job_id)
                    db.session.rollback()
                    status, message = "error", f"{type(exc).__name__}: {exc}"[:500]
                db.session.add(
                    JobRun(job_id=job_id, started_at=started, finished_at=utcnow(),
                           status=status, message=message)
                )
                db.session.commit()
                old = (
                    JobRun.query.filter_by(job_id=job_id)
                    .order_by(JobRun.id.desc())
                    .offset(KEEP_RUNS)
                    .all()
                )
                for r in old:
                    db.session.delete(r)
                db.session.commit()

        return wrapper

    return deco


@tracked("refresh_weather")
def refresh_weather():
    p = weather.refresh()
    return f"{p.get('temp')}°C {p.get('condition')}"


@tracked("refresh_kuma")
def refresh_kuma():
    return f"{kuma.sync()} monitors"


def register(app) -> None:
    global _app
    _app = app
    if not app.config["SCHEDULER_ENABLED"]:
        return
    minutes = settings_minutes(app)
    extra = {"next_run_time": datetime.now(UTC)} if weather_is_stale(app, minutes) else {}
    scheduler.add_job("refresh_weather", "app.jobs:refresh_weather", trigger="interval",
                      minutes=minutes, replace_existing=True, max_instances=1, coalesce=True,
                      **extra)
    scheduler.add_job("refresh_kuma", "app.jobs:refresh_kuma", trigger="interval",
                      seconds=app.config["KUMA_REFRESH_SECONDS"], replace_existing=True,
                      max_instances=1, coalesce=True)


def settings_minutes(app) -> int:
    with app.app_context():
        try:
            return max(5, int(settings.get("weather_refresh_minutes")))
        except Exception:  # noqa: BLE001 - tables may not exist before the first migration
            return 60


def weather_is_stale(app, minutes: int) -> bool:
    with app.app_context():
        try:
            row = db.session.get(WeatherCache, 1)
        except Exception:  # noqa: BLE001
            return False
        return row is None or utcnow() - row.fetched_at > timedelta(minutes=minutes)
