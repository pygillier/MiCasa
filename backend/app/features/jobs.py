"""Scheduled jobs (weather and Uptime Kuma refresh).

Jobs are registered by textual path (``app.features.jobs:name``) so the SQLAlchemy job store can
persist them. Each run is recorded as a ``JobRun`` row via ``tracked``.
"""

from datetime import UTC, datetime, timedelta
from functools import wraps

from loguru import logger

from .. import settings
from ..extensions import db, scheduler
from ..models import JobRun, WeatherCache, utcnow
from . import kuma, weather

KEEP_RUNS = 10
MIN_WEATHER_MINUTES = 5
DEFAULT_WEATHER_MINUTES = 60
_app = None


def _prune_runs(job_id: str) -> None:
    """Delete all but the ``KEEP_RUNS`` most recent runs of ``job_id``."""
    for run in (
        JobRun.query.filter_by(job_id=job_id).order_by(JobRun.id.desc()).offset(KEEP_RUNS).all()
    ):
        db.session.delete(run)
    db.session.commit()


def tracked(job_id: str):
    """Decorator: run the job inside the app context and record a ``JobRun``.

    The job's return value becomes the run message. Exceptions are logged and recorded as
    ``error`` runs rather than propagated, so the scheduler keeps running.
    """

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
                _prune_runs(job_id)

        return wrapper

    return deco


@tracked("refresh_weather")
def refresh_weather():
    """Fetch current weather and store it in ``WeatherCache``."""
    p = weather.refresh()
    return f"{p.get('temp')}°C {p.get('condition')}"


@tracked("refresh_kuma")
def refresh_kuma():
    """Sync monitor states from Uptime Kuma into ``MonitorStatus``."""
    return f"{kuma.sync()} monitors"


def register(app) -> None:
    """Bind the jobs to ``app`` and, when the scheduler is enabled, schedule them.

    The weather job runs immediately if its cache is missing or older than its interval.
    """
    global _app
    _app = app
    if not app.config["SCHEDULER_ENABLED"]:
        return
    minutes = _weather_minutes(app)
    extra = {"next_run_time": datetime.now(UTC)} if _weather_is_stale(app, minutes) else {}
    scheduler.add_job("refresh_weather", "app.features.jobs:refresh_weather", trigger="interval",
                      minutes=minutes, replace_existing=True, max_instances=1, coalesce=True,
                      **extra)
    scheduler.add_job("refresh_kuma", "app.features.jobs:refresh_kuma", trigger="interval",
                      seconds=app.config["KUMA_REFRESH_SECONDS"], replace_existing=True,
                      max_instances=1, coalesce=True)


def _weather_minutes(app) -> int:
    """Configured weather refresh interval, clamped to the minimum."""
    with app.app_context():
        try:
            return max(MIN_WEATHER_MINUTES, int(settings.get("weather_refresh_minutes")))
        except Exception:  # noqa: BLE001 - tables may not exist before the first migration
            return DEFAULT_WEATHER_MINUTES


def _weather_is_stale(app, minutes: int) -> bool:
    """True when there is no cached weather or it is older than ``minutes``."""
    with app.app_context():
        try:
            row = db.session.get(WeatherCache, 1)
        except Exception:  # noqa: BLE001
            return False
        return row is None or utcnow() - row.fetched_at > timedelta(minutes=minutes)
