import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    TESTING = False
    DEBUG = False

    SECRET_KEY = os.getenv("SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.getenv(
        "SECURITY_PASSWORD_SALT", default="59688619562900616051289131821383854197"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL", default="sqlite:////data/micasa.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"

    TIMEZONE = os.getenv("TZ", default="Europe/Paris")
    LOCALE = os.getenv("LOCALE", default="en_US")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProdConfig(Config):
    PREFERRED_URL_SCHEME = "https"
