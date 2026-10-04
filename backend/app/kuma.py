"""Uptime Kuma sync. Only called from the scheduler / admin."""

from flask import current_app
from uptime_kuma_api import UptimeKumaApi

from .extensions import db
from .models import MonitorStatus, utcnow

STATUS_NAMES = {0: "down", 1: "up", 2: "pending", 3: "maintenance"}


def _connect():
    cfg = current_app.config
    if not cfg["KUMA_URL"]:
        raise RuntimeError("KUMA_URL is not configured")
    return UptimeKumaApi(cfg["KUMA_URL"], timeout=15)


def _login(api) -> None:
    cfg = current_app.config
    api.login(cfg["KUMA_USERNAME"], cfg["KUMA_PASSWORD"])


def list_monitors() -> list[dict]:
    with _connect() as api:
        _login(api)
        return [{"id": m["id"], "name": m["name"]} for m in api.get_monitors()]


def sync() -> int:
    with _connect() as api:
        _login(api)
        monitors = api.get_monitors()
        beats = api.get_heartbeats()
    seen = set()
    for m in monitors:
        mid = m["id"]
        seen.add(mid)
        history = beats.get(mid) or []
        if not m.get("active", True):
            status = "paused"
        elif history:
            raw = history[-1]["status"]
            status = STATUS_NAMES.get(int(raw), "pending")
        else:
            status = "pending"
        row = db.session.get(MonitorStatus, mid)
        if row is None:
            row = MonitorStatus(monitor_id=mid)
            db.session.add(row)
        row.name, row.status, row.updated_at = m["name"], status, utcnow()
    for row in MonitorStatus.query.filter(MonitorStatus.monitor_id.notin_(seen or {-1})):
        db.session.delete(row)
    db.session.commit()
    return len(monitors)
