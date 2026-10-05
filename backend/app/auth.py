from functools import wraps

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, current_app, jsonify, redirect, request, session
from loguru import logger

bp = Blueprint("auth", __name__, url_prefix="/api")
oauth = OAuth()


def init_oauth(app) -> None:
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
    return bool(session.get("user"))


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return jsonify(error="unauthorized"), 401
        if request.method not in ("GET", "HEAD", "OPTIONS") and not request.headers.get(
            "X-Requested-With"
        ):
            return jsonify(error="missing X-Requested-With header"), 400
        return fn(*args, **kwargs)

    return wrapper


@bp.get("/me")
def me():
    user = session.get("user")
    return jsonify(authenticated=bool(user), user=user)


@bp.get("/auth/login")
def login():
    client = oauth.create_client("pocketid")
    if client is None:
        return jsonify(error="OIDC not configured"), 503
    session["next"] = "/admin" if request.args.get("next") == "admin" else "/"
    return client.authorize_redirect(redirect_uri())


@bp.get("/auth/callback")
def callback():
    client = oauth.create_client("pocketid")
    if client is None:
        return jsonify(error="OIDC not configured"), 503
    token = client.authorize_access_token()
    userinfo = token.get("userinfo") or client.userinfo(token=token)
    nxt = session.pop("next", "/")
    session.clear()
    session["user"] = {"sub": userinfo.get("sub"), "email": userinfo.get("email"),
                       "name": userinfo.get("name")}
    session.permanent = True
    return redirect(current_app.config["PUBLIC_URL"].rstrip("/") + nxt)


@bp.post("/auth/logout")
def logout():
    if not request.headers.get("X-Requested-With"):
        return jsonify(error="missing X-Requested-With header"), 400
    session.clear()
    return jsonify(ok=True)
