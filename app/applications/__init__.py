from flask import Blueprint

apps = Blueprint("apps", __name__, template_folder="templates")

from . import views  # noqa: E402,F401
