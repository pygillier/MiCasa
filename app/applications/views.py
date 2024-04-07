from flask import render_template
from app.database import db
from app.models.application import Application
from . import apps as bp


@bp.get("/")
def index():
    apps = db.session.execute(db.select(Application).order_by(Application.position)).scalars()
    return render_template("list_apps.html", apps=apps)
