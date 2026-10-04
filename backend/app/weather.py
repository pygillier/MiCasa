"""Google Weather API client. Only called from the scheduler / admin refresh."""

import requests
from flask import current_app

from . import settings
from .extensions import db
from .models import WeatherCache, utcnow

BASE = "https://weather.googleapis.com/v1"


def _deg(node) -> float | None:
    return node.get("degrees") if isinstance(node, dict) else None


def normalize(current: dict, forecast: dict, city: str) -> dict:
    cond = current.get("weatherCondition", {})
    day = (forecast.get("forecastDays") or [{}])[0]
    precip = current.get("precipitation", {}).get("probability", {}).get("percent")
    return {
        "city": city,
        "temp": _deg(current.get("temperature")),
        "feels_like": _deg(current.get("feelsLikeTemperature")),
        "condition_type": cond.get("type", ""),
        "condition": cond.get("description", {}).get("text", ""),
        "high": _deg(day.get("maxTemperature")),
        "low": _deg(day.get("minTemperature")),
        "rain_pct": precip,
        "wind_kmh": current.get("wind", {}).get("speed", {}).get("value"),
        "is_daytime": current.get("isDaytime", True),
    }


def _get(endpoint: str, params: dict, timeout) -> dict:
    """GET a Google Weather endpoint; errors never include the URL (it carries the API key)."""
    try:
        resp = requests.get(f"{BASE}/{endpoint}", params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Google Weather {endpoint} returned HTTP {exc.response.status_code}"
        ) from None
    except requests.RequestException as exc:
        raise RuntimeError(f"Google Weather {endpoint} failed: {type(exc).__name__}") from None


def refresh() -> dict:
    key = settings.get("google_weather_api_key")
    lat, lon = settings.get("weather_lat"), settings.get("weather_lon")
    if not key:
        raise RuntimeError("Google Weather API key is not configured")
    if not lat or not lon:
        raise RuntimeError("Weather location is not configured")
    try:
        lat_f, lon_f = (float(str(v).strip().replace(",", ".")) for v in (lat, lon))
    except ValueError:
        raise RuntimeError("Weather location is invalid") from None
    params = {
        "key": key,
        "location.latitude": lat_f,
        "location.longitude": lon_f,
        "unitsSystem": "METRIC",
        "languageCode": settings.get("weather_language") or "en",
    }
    timeout = current_app.config.get("HTTP_TIMEOUT", 10)
    cur = _get("currentConditions:lookup", params, timeout)
    fc = _get("forecast/days:lookup", {**params, "days": 1}, timeout)
    payload = normalize(cur, fc, settings.get("weather_city"))
    row = db.session.get(WeatherCache, 1)
    if row is None:
        db.session.add(WeatherCache(id=1, payload=payload, fetched_at=utcnow()))
    else:
        row.payload, row.fetched_at = payload, utcnow()
    db.session.commit()
    return payload
