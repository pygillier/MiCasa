import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    TESTING = False
    DEBUG = False

    SECRET_KEY = os.getenv("SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", default='59688619562900616051289131821383854197')

    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL", default="sqlite:////data/micasa.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"


class DevelopmentSettings(Settings):
    DEBUG = True
    TESTING = True


class ProdSettings(Settings):
    pass
