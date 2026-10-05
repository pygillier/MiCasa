import responses

from app import jobs, kuma, weather
from app.extensions import db
from app.models import JobRun, MonitorStatus, WeatherCache

CUR = {
    "temperature": {"degrees": 26.3}, "feelsLikeTemperature": {"degrees": 27.1},
    "weatherCondition": {"type": "CLEAR", "description": {"text": "Clear"}},
    "precipitation": {"probability": {"percent": 10}},
    "wind": {"speed": {"value": 12}},
}
FC = {"forecastDays": [{"maxTemperature": {"degrees": 28}, "minTemperature": {"degrees": 17}}]}


def _configure(app):
    from app import settings
    settings.update({"google_weather_api_key": "k", "weather_lat": "47.2", "weather_lon": "-1.5",
                     "weather_city": "Nantes"})


@responses.activate
def test_weather_refresh_caches(app):
    _configure(app)
    responses.get(f"{weather.BASE}/currentConditions:lookup", json=CUR)
    responses.get(f"{weather.BASE}/forecast/days:lookup", json=FC)
    jobs.refresh_weather()
    p = db.session.get(WeatherCache, 1).payload
    assert (p["temp"], p["high"], p["low"], p["rain_pct"], p["city"]) == (26.3, 28, 17, 10, "Nantes")
    assert JobRun.query.one().status == "ok"


def test_weather_failure_keeps_cache_and_logs(app):
    db.session.add(WeatherCache(id=1, payload={"temp": 1}))
    db.session.commit()
    jobs.refresh_weather()  # no key configured
    assert db.session.get(WeatherCache, 1).payload == {"temp": 1}
    run = JobRun.query.one()
    assert run.status == "error" and "not configured" in run.message


def test_job_runs_pruned_to_ten(app):
    for _ in range(14):
        jobs.refresh_weather()
    assert JobRun.query.filter_by(job_id="refresh_weather").count() == 10


class FakeApi:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def login(self, *a): pass
    def get_monitors(self):
        return [{"id": 1, "name": "A", "active": True}, {"id": 2, "name": "B", "active": True},
                {"id": 3, "name": "C", "active": False}]
    def get_heartbeats(self):
        return {1: [{"status": 0}, {"status": 1}], 2: [{"status": 0}]}


def test_kuma_sync(app, monkeypatch):
    monkeypatch.setattr(kuma, "UptimeKumaApi", FakeApi)
    db.session.add(MonitorStatus(monitor_id=99, status="up"))
    db.session.commit()
    jobs.refresh_kuma()
    got = {m.monitor_id: m.status for m in MonitorStatus.query}
    assert got == {1: "up", 2: "down", 3: "paused"}
