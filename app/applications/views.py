from flask import render_template
from app.database import db
from app.models.application import Application
from . import apps as bp, forms


@bp.get("/")
def index():
    apps = db.session.execute(
        db.select(Application).order_by(Application.position)
    ).scalars()
    return render_template("applications/index.html", apps=apps)


@bp.get("/new")
def add():
    form = forms.ApplicationForm()
    return render_template("applications/new.html", form=form)


@bp.route("/create", methods=["GET", "POST"])
def create():
    pass
