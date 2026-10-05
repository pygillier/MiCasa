from datetime import UTC, datetime

from .extensions import db


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(100), nullable=False, default="")
    position = db.Column(db.Integer, nullable=False, default=0)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    links = db.relationship(
        "Link", back_populates="category", cascade="all, delete-orphan", order_by="Link.position"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "note": self.note,
            "position": self.position,
            "is_public": self.is_public,
        }


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    icon = db.Column(db.String(60), nullable=False, default="ph-link")
    host = db.Column(db.String(100), nullable=False, default="")
    position = db.Column(db.Integer, nullable=False, default=0)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    kuma_monitor_id = db.Column(db.Integer, nullable=True)
    category = db.relationship("Category", back_populates="links")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category_id": self.category_id,
            "label": self.label,
            "url": self.url,
            "icon": self.icon,
            "host": self.host,
            "position": self.position,
            "is_public": self.is_public,
            "kuma_monitor_id": self.kuma_monitor_id,
        }


class Setting(db.Model):
    key = db.Column(db.String(60), primary_key=True)
    value = db.Column(db.Text, nullable=False, default="")


class JobRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(60), nullable=False, index=True)
    started_at = db.Column(db.DateTime, nullable=False)
    finished_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), nullable=False)
    message = db.Column(db.Text, nullable=False, default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "started_at": self.started_at.isoformat() + "Z",
            "finished_at": self.finished_at.isoformat() + "Z",
            "status": self.status,
            "message": self.message,
        }


class WeatherCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payload = db.Column(db.JSON, nullable=False)
    fetched_at = db.Column(db.DateTime, nullable=False, default=utcnow)


class MonitorStatus(db.Model):
    monitor_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(200), nullable=False, default="")
    status = db.Column(db.String(20), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow)
