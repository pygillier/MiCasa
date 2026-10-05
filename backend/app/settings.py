"""DB-backed settings with env fallbacks."""

from flask import current_app

from .extensions import db
from .models import Setting

DEFAULTS = {
    "weather_city": "",
    "weather_lat": "",
    "weather_lon": "",
    "weather_language": "en",
    "weather_refresh_minutes": "60",
    "kuma_base_url": "",
    "theme": "nocturne",
    "google_weather_api_key": "",
}
# Keep in sync with frontend/lib/themes.ts.
THEMES = {"nocturne", "home"}
# Never serialized back to clients.
SECRET_KEYS = {"google_weather_api_key"}


def get(key: str) -> str:
    row = db.session.get(Setting, key)
    if row is not None and row.value != "":
        return row.value
    if key == "google_weather_api_key":
        return current_app.config.get("GOOGLE_WEATHER_API_KEY", "")
    if key == "theme" and (row is None or row.value not in THEMES):
        return DEFAULTS["theme"]
    if key == "kuma_base_url":
        return current_app.config.get("KUMA_URL", "")
    return DEFAULTS.get(key, "")


def put(key: str, value: str) -> None:
    row = db.session.get(Setting, key)
    if row is None:
        db.session.add(Setting(key=key, value=value))
    else:
        row.value = value


def public_view() -> dict:
    out = {k: get(k) for k in DEFAULTS if k not in SECRET_KEYS}
    secret = get("google_weather_api_key")
    out["google_weather_api_key_configured"] = bool(secret)
    out["google_weather_api_key_tail"] = secret[-4:] if secret else ""
    return out


def update(data: dict) -> None:
    for key, value in data.items():
        if key not in DEFAULTS:
            continue
        value = "" if value is None else str(value).strip()
        if key == "theme" and value not in THEMES:
            continue
        # An empty secret means "keep the current one".
        if key in SECRET_KEYS and value == "":
            continue
        put(key, value)
    db.session.commit()
