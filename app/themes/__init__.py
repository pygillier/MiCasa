from flask import Blueprint


themes = Blueprint("themes", __name__, template_folder="templates")

from . import views  # noqa: E402,F401
