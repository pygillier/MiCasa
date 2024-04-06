from flask import render_template
from app.database import db
from app.models.theme import Theme
from . import themes as bp


@bp.get("/")
def index():
    themes = db.session.execute(db.select(Theme).order_by(Theme.name)).scalars()
    return render_template("index.html", themes=themes)
