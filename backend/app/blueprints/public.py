"""Public (anonymous-readable) API endpoints under ``/api``."""

from flask import Blueprint, jsonify

from .. import settings
from ..auth import is_authenticated
from ..extensions import db
from ..models import Category, Link, MonitorStatus, WeatherCache, iso_z

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/theme")
def theme():
    """Active UI themes: ``theme`` for dark / night, ``theme_day`` for light / day."""
    return jsonify(theme=settings.get("theme"), theme_day=settings.get("theme_day"))


def _startpage_item(link: Link, authed: bool, statuses: dict, kuma_base: str) -> dict:
    """Serialize one link; status fields are only ever added for authenticated users."""
    item = {"id": link.id, "label": link.label, "url": link.url,
            "icon": link.icon, "host": link.host}
    if authed and link.kuma_monitor_id is not None:
        item["status"] = statuses.get(link.kuma_monitor_id, "pending")
        if kuma_base:
            item["status_url"] = f"{kuma_base}/dashboard/{link.kuma_monitor_id}"
    return item


@bp.get("/startpage")
def startpage():
    """Categories with their links, filtered server-side by visibility.

    Anonymous users get only public categories/links (and categories left empty by that
    filter are dropped) and never any monitor status. Authenticated users get everything.
    """
    authed = is_authenticated()
    statuses, kuma_base = {}, ""
    if authed:
        statuses = {m.monitor_id: m.status for m in MonitorStatus.query.all()}
        kuma_base = settings.get("kuma_base_url").rstrip("/")
    query = Category.query.order_by(Category.position, Category.id)
    if not authed:
        query = query.filter_by(is_public=True)
    groups = []
    for cat in query:
        items = [
            _startpage_item(link, authed, statuses, kuma_base)
            for link in cat.links
            if authed or link.is_public
        ]
        if items or authed:
            groups.append({"id": cat.id, "name": cat.name, "note": cat.note, "items": items})
    return jsonify(authenticated=authed, groups=groups)


@bp.get("/weather")
def get_weather():
    """Cached weather (never calls Google). ``enabled`` is false without an API key."""
    if not settings.get("google_weather_api_key").strip():
        return jsonify(enabled=False, weather=None)
    row = db.session.get(WeatherCache, 1)
    if row is None:
        return jsonify(enabled=True, weather=None)
    return jsonify(enabled=True, weather=row.payload, fetched_at=iso_z(row.fetched_at))
