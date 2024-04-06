import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    TESTING = False
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL", default="sqlite:////data/micasa.db")


class DevelopmentSettings(Settings):
    DEBUG = True
    TESTING = True


class ProdSettings(Settings):
    pass
