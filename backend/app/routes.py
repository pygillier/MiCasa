from urllib.parse import urlparse

from flask import Blueprint, Response, jsonify, request

from . import jobs, kuma, opml, settings
from .auth import is_authenticated, login_required
from .extensions import db
from .models import Category, JobRun, Link, MonitorStatus, WeatherCache

bp = Blueprint("api", __name__, url_prefix="/api")
admin = Blueprint("admin", __name__, url_prefix="/api/admin")


# ---------- public ----------
@bp.get("/theme")
def theme():
    return jsonify(theme=settings.get("theme"))


@bp.get("/startpage")
def startpage():
    authed = is_authenticated()
    statuses = {}
    kuma_base = ""
    if authed:
        statuses = {m.monitor_id: m.status for m in MonitorStatus.query.all()}
        kuma_base = settings.get("kuma_base_url").rstrip("/")
    query = Category.query.order_by(Category.position, Category.id)
    if not authed:
        query = query.filter_by(is_public=True)
    groups = []
    for cat in query:
        items = []
        for link in cat.links:
            if not authed and not link.is_public:
                continue
            item = {"id": link.id, "label": link.label, "url": link.url,
                    "icon": link.icon, "host": link.host}
            if authed and link.kuma_monitor_id is not None:
                item["status"] = statuses.get(link.kuma_monitor_id, "pending")
                if kuma_base:
                    item["status_url"] = f"{kuma_base}/dashboard/{link.kuma_monitor_id}"
            items.append(item)
        if items or authed:
            groups.append({"id": cat.id, "name": cat.name, "note": cat.note, "items": items})
    return jsonify(authenticated=authed, groups=groups)


@bp.get("/weather")
def get_weather():
    if not settings.get("google_weather_api_key").strip():
        return jsonify(enabled=False, weather=None)
    row = db.session.get(WeatherCache, 1)
    if row is None:
        return jsonify(enabled=True, weather=None)
    return jsonify(enabled=True, weather=row.payload, fetched_at=row.fetched_at.isoformat() + "Z")


# ---------- admin: categories ----------
def _bool(v) -> bool:
    return bool(v)


def _next_position(model, **flt) -> int:
    last = model.query.filter_by(**flt).order_by(model.position.desc()).first()
    return (last.position + 1) if last else 0


@admin.get("/categories")
@login_required
def list_categories():
    cats = Category.query.order_by(Category.position, Category.id).all()
    return jsonify([c.to_dict() for c in cats])


@admin.post("/categories")
@login_required
def create_category():
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify(error="name is required"), 422
    cat = Category(name=name[:100], note=(d.get("note") or "")[:100],
                   is_public=_bool(d.get("is_public")), position=_next_position(Category))
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


@admin.put("/categories/reorder")
@login_required
def reorder_categories():
    return _reorder(Category, request.get_json(silent=True) or {})


@admin.put("/categories/<int:cid>")
@login_required
def update_category(cid):
    cat = db.get_or_404(Category, cid)
    d = request.get_json(silent=True) or {}
    if "name" in d:
        if not (d["name"] or "").strip():
            return jsonify(error="name is required"), 422
        cat.name = d["name"].strip()[:100]
    if "note" in d:
        cat.note = (d["note"] or "")[:100]
    if "is_public" in d:
        cat.is_public = _bool(d["is_public"])
    db.session.commit()
    return jsonify(cat.to_dict())


@admin.delete("/categories/<int:cid>")
@login_required
def delete_category(cid):
    db.session.delete(db.get_or_404(Category, cid))
    db.session.commit()
    return "", 204


# ---------- admin: links ----------
def _valid_url(url: str) -> bool:
    p = urlparse(url)
    return p.scheme in ("http", "https") and bool(p.netloc)


def _apply_link(link: Link, d: dict):
    if "label" in d:
        if not (d["label"] or "").strip():
            return "label is required"
        link.label = d["label"].strip()[:100]
    if "url" in d:
        if not _valid_url(d["url"] or ""):
            return "url must be http(s)"
        link.url = d["url"].strip()
        if "host" not in d and not link.host:
            link.host = urlparse(link.url).netloc
    if "host" in d:
        link.host = (d["host"] or "")[:100] or urlparse(link.url).netloc
    if "icon" in d:
        icon = (d["icon"] or "ph-link").strip()
        if not icon.startswith("ph-") or not icon.replace("-", "").isalnum():
            return "icon must be a Phosphor class like ph-house"
        link.icon = icon
    if "is_public" in d:
        link.is_public = _bool(d["is_public"])
    if "kuma_monitor_id" in d:
        v = d["kuma_monitor_id"]
        link.kuma_monitor_id = int(v) if v not in (None, "") else None
    if "category_id" in d:
        if db.session.get(Category, d["category_id"]) is None:
            return "unknown category"
        link.category_id = d["category_id"]
    return None


@admin.get("/links")
@login_required
def list_links():
    links = Link.query.order_by(Link.category_id, Link.position, Link.id).all()
    return jsonify([link.to_dict() for link in links])


@admin.post("/links")
@login_required
def create_link():
    d = request.get_json(silent=True) or {}
    link = Link(position=0)
    if not d.get("label") or not d.get("url") or not d.get("category_id"):
        return jsonify(error="label, url and category_id are required"), 422
    err = _apply_link(link, d)
    if err:
        return jsonify(error=err), 422
    link.position = _next_position(Link, category_id=link.category_id)
    db.session.add(link)
    db.session.commit()
    return jsonify(link.to_dict()), 201


@admin.put("/links/reorder")
@login_required
def reorder_links():
    return _reorder(Link, request.get_json(silent=True) or {})


@admin.put("/links/<int:lid>")
@login_required
def update_link(lid):
    link = db.get_or_404(Link, lid)
    err = _apply_link(link, request.get_json(silent=True) or {})
    if err:
        db.session.rollback()
        return jsonify(error=err), 422
    db.session.commit()
    return jsonify(link.to_dict())


@admin.delete("/links/<int:lid>")
@login_required
def delete_link(lid):
    db.session.delete(db.get_or_404(Link, lid))
    db.session.commit()
    return "", 204


def _reorder(model, d: dict):
    ids = d.get("ids")
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify(error="ids must be a list of integers"), 422
    for pos, i in enumerate(ids):
        row = db.session.get(model, i)
        if row is not None:
            row.position = pos
    db.session.commit()
    return jsonify(ok=True)


# ---------- admin: kuma, settings, jobs ----------
@admin.get("/kuma/monitors")
@login_required
def kuma_monitors():
    try:
        return jsonify(kuma.list_monitors())
    except Exception as exc:  # noqa: BLE001
        return jsonify(error=f"Uptime Kuma unavailable: {exc}"), 502


@admin.get("/settings")
@login_required
def get_settings():
    return jsonify(settings.public_view())


@admin.put("/settings")
@login_required
def put_settings():
    settings.update(request.get_json(silent=True) or {})
    return jsonify(settings.public_view())


@admin.post("/weather/refresh")
@login_required
def refresh_weather_now():
    jobs.refresh_weather()
    last = JobRun.query.filter_by(job_id="refresh_weather").order_by(JobRun.id.desc()).first()
    code = 200 if last and last.status == "ok" else 502
    return jsonify(last.to_dict() if last else {}), code


@admin.get("/jobs")
@login_required
def list_jobs():
    runs = JobRun.query.order_by(JobRun.id.desc()).limit(40).all()
    return jsonify([r.to_dict() for r in runs])


# ---------- admin: OPML import/export ----------
@admin.get("/export.opml")
@login_required
def export_opml():
    return Response(opml.export_opml(), mimetype="text/x-opml",
                    headers={"Content-Disposition": 'attachment; filename="micasa.opml"'})


@admin.post("/import")
@login_required
def import_opml():
    try:
        return jsonify(opml.import_opml(request.get_data(cache=False)))
    except opml.OpmlError as exc:
        db.session.rollback()
        return jsonify(error=str(exc)), 422
