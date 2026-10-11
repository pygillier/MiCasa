"""Runtime settings stored in the DB, with environment/config fallbacks and built-in defaults.

Values are strings; an empty stored value means "not set". Lookup order: DB value,
``Flask.config`` fallback (see ``ENV_FALLBACKS``), then ``DEFAULTS``.
"""

from flask import current_app

from .extensions import db
from .models import Setting

DEFAULTS = {
    "site_title": "MiCasa",  # homepage / browser tab title; blank falls back to this
    "weather_city": "",
    "weather_lat": "",
    "weather_lon": "",
    "weather_language": "en",
    "weather_refresh_minutes": "60",
    "kuma_base_url": "",
    "theme": "nocturne",  # used at night / when the OS prefers dark
    "theme_day": "home-day",  # used by day / when the OS prefers light
    "google_weather_api_key": "",
}
# Keep in sync with frontend/lib/themes.ts.
THEMES = {"nocturne", "home", "home-day"}
THEME_KEYS = {"theme", "theme_day"}
# Never serialized back to clients.
SECRET_KEYS = {"google_weather_api_key"}
# Setting key -> app.config key used when the DB has no value.
ENV_FALLBACKS = {"google_weather_api_key": "GOOGLE_WEATHER_API_KEY", "kuma_base_url": "KUMA_URL"}


def get(key: str) -> str:
    """Effective value of ``key`` (``""`` for unknown keys)."""
    row = db.session.get(Setting, key)
    if row is not None and row.value != "":
        return row.value
    if key in ENV_FALLBACKS:
        return current_app.config.get(ENV_FALLBACKS[key], "")
    return DEFAULTS.get(key, "")


def put(key: str, value: str) -> None:
    """Stage ``value`` for ``key`` (upsert); the caller commits."""
    row = db.session.get(Setting, key)
    if row is None:
        db.session.add(Setting(key=key, value=value))
    else:
        row.value = value


def public_view() -> dict:
    """All settings safe to send to the admin UI; the API key is reduced to a configured flag and its last 4 chars."""
    out = {k: get(k) for k in DEFAULTS if k not in SECRET_KEYS}
    secret = get("google_weather_api_key")
    out["google_weather_api_key_configured"] = bool(secret)
    out["google_weather_api_key_tail"] = secret[-4:] if secret else ""
    return out


def update(data: dict) -> None:
    """Apply a partial update and commit. Unknown keys and invalid themes are ignored; blank secrets keep the current value."""
    for key, value in data.items():
        if key not in DEFAULTS:
            continue
        value = "" if value is None else str(value).strip()
        if key in THEME_KEYS and value not in THEMES:
            continue
        # An empty secret means "keep the current one".
        if key in SECRET_KEYS and value == "":
            continue
        put(key, value)
    db.session.commit()
