from flask import render_template
from . import home as bp


@bp.get("/")
def index():
    return render_template("home/index.html")
