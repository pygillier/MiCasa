from app.extensions import db
from app.models import MonitorStatus, WeatherCache, utcnow

from .conftest import H


def test_anonymous_sees_only_public(client):
    data = client.get("/api/startpage").get_json()
    assert [g["name"] for g in data["groups"]] == ["Public"]
    items = data["groups"][0]["items"]
    assert [i["label"] for i in items] == ["Open"]
    assert "status" not in items[0]


def test_authenticated_sees_everything_with_status(app, authed):
    db.session.add(MonitorStatus(monitor_id=1, status="up"))
    db.session.commit()
    data = authed.get("/api/startpage").get_json()
    assert [g["name"] for g in data["groups"]] == ["Public", "Private"]
    open_link = data["groups"][0]["items"][0]
    assert open_link["status"] == "up"
    assert len(data["groups"][0]["items"]) == 2


def test_admin_requires_auth(client):
    assert client.get("/api/admin/links").status_code == 401
    assert client.post("/api/admin/categories", json={"name": "x"}, headers=H).status_code == 401


def test_admin_write_requires_header(authed):
    assert authed.post("/api/admin/categories", json={"name": "x"}).status_code == 400


def test_category_and_link_crud(authed):
    r = authed.post("/api/admin/categories", json={"name": "New", "is_public": True}, headers=H)
    cid = r.get_json()["id"]
    r = authed.post("/api/admin/links", headers=H,
                    json={"label": "L", "url": "https://x.test/p", "category_id": cid,
                          "icon": "ph-house"})
    assert r.status_code == 201 and r.get_json()["host"] == "x.test"
    lid = r.get_json()["id"]
    assert authed.put(f"/api/admin/links/{lid}", json={"url": "javascript:alert(1)"},
                      headers=H).status_code == 422
    assert authed.put(f"/api/admin/links/{lid}", json={"icon": "<b>"},
                      headers=H).status_code == 422
    assert authed.delete(f"/api/admin/categories/{cid}", headers=H).status_code == 204
    assert authed.get("/api/admin/links").get_json()[-1]["label"] != "L"


def test_reorder(authed):
    ids = [c["id"] for c in authed.get("/api/admin/categories").get_json()]
    authed.put("/api/admin/categories/reorder", json={"ids": ids[::-1]}, headers=H)
    assert [c["id"] for c in authed.get("/api/admin/categories").get_json()] == ids[::-1]


def test_settings_never_expose_api_key(authed):
    r = authed.put("/api/admin/settings", headers=H,
                   json={"google_weather_api_key": "SECRETKEY1234", "weather_city": "Nantes"})
    body = r.get_json()
    assert "google_weather_api_key" not in body
    assert body["google_weather_api_key_configured"] is True
    assert body["google_weather_api_key_tail"] == "1234"
    # empty value keeps the existing secret
    r = authed.put("/api/admin/settings", headers=H, json={"google_weather_api_key": ""})
    assert r.get_json()["google_weather_api_key_configured"] is True


def test_weather_disabled_without_api_key(client):
    assert client.get("/api/weather").get_json() == {"enabled": False, "weather": None}


def test_weather_endpoint_reads_cache(client, app):
    app.config["GOOGLE_WEATHER_API_KEY"] = "k"
    assert client.get("/api/weather").get_json() == {"enabled": True, "weather": None}
    db.session.add(WeatherCache(id=1, payload={"temp": 20}, fetched_at=utcnow()))
    db.session.commit()
    assert client.get("/api/weather").get_json()["weather"] == {"temp": 20}


def test_theme_is_public_validated_and_persisted(client, authed):
    assert client.get("/api/theme").get_json() == {"theme": "nocturne"}
    authed.put("/api/admin/settings", headers=H, json={"theme": "home"})
    assert client.get("/api/theme").get_json() == {"theme": "home"}
    # unknown themes are ignored
    authed.put("/api/admin/settings", headers=H, json={"theme": "<script>"})
    assert client.get("/api/theme").get_json() == {"theme": "home"}


def test_theme_change_requires_auth(app):
    anon = app.test_client()
    assert anon.put("/api/admin/settings", headers=H, json={"theme": "home"}).status_code in (401, 403)
