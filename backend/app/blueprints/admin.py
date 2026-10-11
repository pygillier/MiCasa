"""Authenticated admin API under ``/api/admin``: categories, links, settings, jobs, OPML."""

from urllib.parse import urlparse

from flask import Blueprint, Response, jsonify, request

from .. import settings
from ..auth import login_required
from ..extensions import db
from ..features import about, jobs, kuma, opml
from ..models import Category, JobRun, Link, MonitorStatus, next_position
from ..validation import is_http_url, is_phosphor_icon

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

NAME_MAX = 100  # label / category name / note / host column width


def _body() -> dict:
    """JSON request body, or ``{}`` when absent or malformed."""
    return request.get_json(silent=True) or {}


def _error(message: str, status: int = 422):
    return jsonify(error=message), status


def _delete(model, row_id: int):
    """Delete a row by primary key (404 if missing); shared by the DELETE endpoints."""
    db.session.delete(db.get_or_404(model, row_id))
    db.session.commit()
    return "", 204


def _reorder(model, data: dict):
    """Set ``position`` from the order of ``data["ids"]``; unknown ids are ignored."""
    ids = data.get("ids")
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return _error("ids must be a list of integers")
    for pos, row_id in enumerate(ids):
        row = db.session.get(model, row_id)
        if row is not None:
            row.position = pos
    db.session.commit()
    return jsonify(ok=True)


# ---------- admin: categories ----------
@bp.get("/categories")
@login_required
def list_categories():
    cats = Category.query.order_by(Category.position, Category.id).all()
    return jsonify([c.to_dict() for c in cats])


@bp.post("/categories")
@login_required
def create_category():
    d = _body()
    name = (d.get("name") or "").strip()
    if not name:
        return _error("name is required")
    cat = Category(name=name[:NAME_MAX], note=(d.get("note") or "")[:NAME_MAX],
                   is_public=bool(d.get("is_public")), position=next_position(Category))
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


@bp.put("/categories/reorder")
@login_required
def reorder_categories():
    return _reorder(Category, _body())


@bp.put("/categories/<int:cid>")
@login_required
def update_category(cid):
    cat = db.get_or_404(Category, cid)
    d = _body()
    if "name" in d:
        if not (d["name"] or "").strip():
            return _error("name is required")
        cat.name = d["name"].strip()[:NAME_MAX]
    if "note" in d:
        cat.note = (d["note"] or "")[:NAME_MAX]
    if "is_public" in d:
        cat.is_public = bool(d["is_public"])
    db.session.commit()
    return jsonify(cat.to_dict())


@bp.delete("/categories/<int:cid>")
@login_required
def delete_category(cid):
    return _delete(Category, cid)


# ---------- admin: links ----------
def _apply_link(link: Link, d: dict) -> str | None:
    """Copy the fields present in ``d`` onto ``link``, validating them.

    Returns an error message for the first invalid field, ``None`` on success. The caller
    must roll back the session on error since earlier fields may already be assigned.
    """
    if "label" in d:
        if not (d["label"] or "").strip():
            return "label is required"
        link.label = d["label"].strip()[:NAME_MAX]
    if "url" in d:
        if not is_http_url(d["url"] or ""):
            return "url must be http(s)"
        link.url = d["url"].strip()
        if "host" not in d and not link.host:
            link.host = urlparse(link.url).netloc
    if "host" in d:
        link.host = (d["host"] or "")[:NAME_MAX] or urlparse(link.url).netloc
    if "icon" in d:
        icon = (d["icon"] or "ph-link").strip()
        if not is_phosphor_icon(icon):
            return "icon must be a Phosphor class like ph-house"
        link.icon = icon
    if "is_public" in d:
        link.is_public = bool(d["is_public"])
    if "kuma_monitor_id" in d:
        v = d["kuma_monitor_id"]
        link.kuma_monitor_id = int(v) if v not in (None, "") else None
    if "category_id" in d:
        if db.session.get(Category, d["category_id"]) is None:
            return "unknown category"
        link.category_id = d["category_id"]
    return None


@bp.get("/links")
@login_required
def list_links():
    links = Link.query.order_by(Link.category_id, Link.position, Link.id).all()
    statuses = {m.monitor_id: m.status for m in MonitorStatus.query.all()}
    return jsonify(
        [
            {**link.to_dict(), "monitor_status": statuses.get(link.kuma_monitor_id, "pending")}
            if link.kuma_monitor_id is not None
            else link.to_dict()
            for link in links
        ]
    )


@bp.post("/links")
@login_required
def create_link():
    d = _body()
    if not d.get("label") or not d.get("url") or not d.get("category_id"):
        return _error("label, url and category_id are required")
    link = Link(position=0)
    if err := _apply_link(link, d):
        return _error(err)
    link.position = next_position(Link, category_id=link.category_id)
    db.session.add(link)
    db.session.commit()
    return jsonify(link.to_dict()), 201


@bp.put("/links/reorder")
@login_required
def reorder_links():
    return _reorder(Link, _body())


@bp.put("/links/<int:lid>")
@login_required
def update_link(lid):
    link = db.get_or_404(Link, lid)
    if err := _apply_link(link, _body()):
        db.session.rollback()
        return _error(err)
    db.session.commit()
    return jsonify(link.to_dict())


@bp.delete("/links/<int:lid>")
@login_required
def delete_link(lid):
    return _delete(Link, lid)


# ---------- admin: kuma, settings, jobs ----------
@bp.get("/kuma/monitors")
@login_required
def kuma_monitors():
    """Live monitor list from Uptime Kuma (for the link editor's picker)."""
    try:
        return jsonify(kuma.list_monitors())
    except Exception as exc:  # noqa: BLE001
        return _error(f"Uptime Kuma unavailable: {exc}", 502)


@bp.get("/settings")
@login_required
def get_settings():
    return jsonify(settings.public_view())


@bp.put("/settings")
@login_required
def put_settings():
    settings.update(_body())
    return jsonify(settings.public_view())


@bp.post("/weather/refresh")
@login_required
def refresh_weather_now():
    """Run the weather job synchronously; responds with its JobRun (502 if it failed)."""
    jobs.refresh_weather()
    last = JobRun.query.filter_by(job_id="refresh_weather").order_by(JobRun.id.desc()).first()
    code = 200 if last and last.status == "ok" else 502
    return jsonify(last.to_dict() if last else {}), code


@bp.get("/jobs")
@login_required
def list_jobs():
    """Most recent job runs across all jobs, newest first."""
    runs = JobRun.query.order_by(JobRun.id.desc()).limit(40).all()
    return jsonify([r.to_dict() for r in runs])


# ---------- admin: about ----------
@bp.get("/about")
@login_required
def get_about():
    return jsonify(version=about.backend_version())


# ---------- admin: OPML import/export ----------
@bp.get("/export.opml")
@login_required
def export_opml():
    return Response(opml.export_opml(), mimetype="text/x-opml",
                    headers={"Content-Disposition": 'attachment; filename="micasa.opml"'})


@bp.post("/import")
@login_required
def import_opml():
    try:
        return jsonify(opml.import_opml(request.get_data(cache=False)))
    except opml.OpmlError as exc:
        db.session.rollback()
        return _error(str(exc))
