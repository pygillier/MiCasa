from flask import Blueprint


themes = Blueprint("themes", __name__)

from . import views  # noqa: E402,F401
