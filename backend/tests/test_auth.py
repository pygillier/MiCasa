def test_me_anonymous(client):
    assert client.get("/api/me").get_json()["authenticated"] is False


def test_me_authenticated(authed):
    assert authed.get("/api/me").get_json()["authenticated"] is True


def test_logout_clears_session(authed):
    assert authed.post("/api/auth/logout", headers={"X-Requested-With": "t"}).status_code == 200
    assert authed.get("/api/me").get_json()["authenticated"] is False


def test_pkce_configured(app):
    from app.auth import oauth
    client = oauth.create_client("pocketid")
    assert client.client_kwargs["code_challenge_method"] == "S256"


def test_redirect_uri_uses_public_url_not_backend_host(app):
    from app.auth import redirect_uri
    app.config["PUBLIC_URL"] = "https://start.example.com/"
    with app.test_request_context(base_url="http://localhost:5000"):
        assert redirect_uri() == "https://start.example.com/api/auth/callback"
