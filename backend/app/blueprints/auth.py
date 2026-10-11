"""Login/logout and session endpoints under ``/api`` (OIDC with PocketID)."""

from flask import Blueprint, current_app, jsonify, redirect, request, session

from ..auth import missing_xhr_header, oauth, redirect_uri

bp = Blueprint("auth", __name__, url_prefix="/api")


@bp.get("/me")
def me():
    """Current session user (``authenticated`` false and ``user`` null when anonymous)."""
    user = session.get("user")
    return jsonify(authenticated=bool(user), user=user)


@bp.get("/auth/login")
def login():
    """Start the OIDC flow; ``?next=admin`` returns to the admin page afterwards."""
    client = oauth.create_client("pocketid")
    if client is None:
        return jsonify(error="OIDC not configured"), 503
    session["next"] = "/admin" if request.args.get("next") == "admin" else "/"
    return client.authorize_redirect(redirect_uri())


@bp.get("/auth/callback")
def callback():
    """Finish the OIDC flow: store the identity in a fresh session and redirect to the frontend.

    Any identity the IdP authenticates for this client is accepted (single-user app).
    """
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
    """Clear the session (requires ``X-Requested-With``)."""
    if err := missing_xhr_header():
        return err
    session.clear()
    return jsonify(ok=True)
