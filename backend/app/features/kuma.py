"""Uptime Kuma sync. Only called from the scheduler / admin."""

from contextlib import contextmanager

from flask import current_app
from uptime_kuma_api import UptimeKumaApi

from ..extensions import db
from ..models import MonitorStatus, utcnow

STATUS_NAMES = {0: "down", 1: "up", 2: "pending", 3: "maintenance"}


@contextmanager
def _session():
    """Logged-in Kuma API connection, closed on exit (also when login fails)."""
    cfg = current_app.config
    if not cfg["KUMA_URL"]:
        raise RuntimeError("KUMA_URL is not configured")
    with UptimeKumaApi(cfg["KUMA_URL"], timeout=15) as api:
        api.login(cfg["KUMA_USERNAME"], cfg["KUMA_PASSWORD"])
        yield api


def _status(monitor: dict, history: list[dict]) -> str:
    """Dot status for a monitor: ``paused`` if inactive, else its latest heartbeat, else ``pending``."""
    if not monitor.get("active", True):
        return "paused"
    if history:
        return STATUS_NAMES.get(int(history[-1]["status"]), "pending")
    return "pending"


def list_monitors() -> list[dict]:
    """``{id, name}`` for every monitor, fetched live from Kuma."""
    with _session() as api:
        return [{"id": m["id"], "name": m["name"]} for m in api.get_monitors()]


def sync() -> list[str]:
    """Mirror Kuma monitor states into ``MonitorStatus``; drops rows of deleted monitors.

    Returns a description of each change since the previous sync (new, removed or re-stated
    monitors); empty when nothing changed.
    """
    with _session() as api:
        monitors = api.get_monitors()
        beats = api.get_heartbeats()
    seen, changes = set(), []
    for m in monitors:
        mid = m["id"]
        seen.add(mid)
        status = _status(m, beats.get(mid) or [])
        row = db.session.get(MonitorStatus, mid)
        if row is None:
            row = MonitorStatus(monitor_id=mid)
            db.session.add(row)
            changes.append(f"{m['name']}: new ({status})")
        elif row.status != status:
            changes.append(f"{m['name']}: {row.status} -> {status}")
        row.name, row.status, row.updated_at = m["name"], status, utcnow()
    for row in MonitorStatus.query.filter(MonitorStatus.monitor_id.notin_(seen or {-1})):
        changes.append(f"{row.name}: removed")
        db.session.delete(row)
    db.session.commit()
    return changes
