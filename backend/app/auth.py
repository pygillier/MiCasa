"""OIDC client setup and session helpers. The HTTP routes live in ``blueprints/auth.py``."""

from functools import wraps

from authlib.integrations.flask_client import OAuth
from flask import current_app, jsonify, request, session
from loguru import logger

oauth = OAuth()


def init_oauth(app) -> None:
    """Register the ``pocketid`` OAuth client when ``OIDC_ISSUER`` is configured."""
    oauth.init_app(app)
    if app.config["OIDC_ISSUER"]:
        oauth.register(
            "pocketid",
            client_id=app.config["OIDC_CLIENT_ID"],
            client_secret=app.config["OIDC_CLIENT_SECRET"],
            server_metadata_url=app.config["OIDC_ISSUER"].rstrip("/")
            + "/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid email profile",
                "code_challenge_method": "S256",  # PKCE
            },
        )
        logger.info("OAuth client 'pocketid' registered with issuer: {}", app.config["OIDC_ISSUER"])


def redirect_uri() -> str:
    """Callback URL as seen by the browser: the frontend origin, not the Flask host."""
    return current_app.config["PUBLIC_URL"].rstrip("/") + "/api/auth/callback"


def is_authenticated() -> bool:
    """True when the session holds a logged-in user."""
    return bool(session.get("user"))


def missing_xhr_header():
    """400 response when the CSRF-guard ``X-Requested-With`` header is absent, else ``None``."""
    if not request.headers.get("X-Requested-With"):
        return jsonify(error="missing X-Requested-With header"), 400
    return None


def login_required(fn):
    """Require an authenticated session; state-changing methods also need ``X-Requested-With``."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return jsonify(error="unauthorized"), 401
        if request.method not in ("GET", "HEAD", "OPTIONS") and (err := missing_xhr_header()):
            return err
        return fn(*args, **kwargs)

    return wrapper
