from flask import render_template, make_response, redirect, url_for
from app.database import db
from app.models.theme import Theme
from . import themes as bp


@bp.get("/")
def index():
    themes = db.session.execute(db.select(Theme).order_by(Theme.name)).scalars()
    return render_template("index.html", themes=themes)


@bp.get("/themes.css")
def stylesheet():
    themes = db.session.execute(db.select(Theme).order_by(Theme.name)).scalars()
    resp = make_response(render_template("styles.css", themes=themes), 200)
    resp.headers['Content-Type'] = 'text/css'
    return resp


@bp.get("/select/<int:theme_id>")
def select_theme(theme_id):
    return redirect(url_for("themes.index"))


@bp.get("/new")
def new():
    pass
