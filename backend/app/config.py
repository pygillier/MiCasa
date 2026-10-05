import os
from pathlib import Path

_DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "micasa.db"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{_DEFAULT_DB}")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("PUBLIC_URL", "").startswith("https://")

    OIDC_ISSUER = os.environ.get("OIDC_ISSUER", "")
    OIDC_CLIENT_ID = os.environ.get("OIDC_CLIENT_ID", "")
    OIDC_CLIENT_SECRET = os.environ.get("OIDC_CLIENT_SECRET", "")
    PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:3000")

    GOOGLE_WEATHER_API_KEY = os.environ.get("GOOGLE_WEATHER_API_KEY", "")
    KUMA_URL = os.environ.get("KUMA_URL", "")
    KUMA_USERNAME = os.environ.get("KUMA_USERNAME", "")
    KUMA_PASSWORD = os.environ.get("KUMA_PASSWORD", "")

    SCHEDULER_ENABLED = os.environ.get("SCHEDULER_ENABLED", "1") == "1"
    SCHEDULER_API_ENABLED = False
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_JSON = os.environ.get("LOG_JSON", "0") == "1"
    KUMA_REFRESH_SECONDS = 60


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SCHEDULER_ENABLED = False
    GOOGLE_WEATHER_API_KEY = ""
    OIDC_ISSUER = "https://id.example.test"
    OIDC_CLIENT_ID = "cid"
    OIDC_CLIENT_SECRET = "secret"
    KUMA_URL = "http://kuma.test"
    KUMA_USERNAME = "u"
    KUMA_PASSWORD = "p"
