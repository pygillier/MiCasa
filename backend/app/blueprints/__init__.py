"""HTTP blueprints. One module per concern, each exposing a ``bp`` Blueprint."""

from flask import Flask

from . import admin, auth, public


def register_blueprints(app: Flask) -> None:
    """Attach every blueprint to ``app``."""
    for module in (auth, public, admin):
        app.register_blueprint(module.bp)
