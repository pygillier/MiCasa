from pathlib import Path
import environ
import os

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    DATABASE_URL=(str, "sqlite:////data/micasa.db"),
    TIMEZONE=(str, "Europe/Paris"),
    APP_URL=(str, None),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if present
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = [
    "127.0.0.1",
]

if env("APP_URL") is not None:
    CSRF_TRUSTED_ORIGINS = [env("APP_URL")]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",  # Let whitenoise handle static even in dev
    "django.contrib.staticfiles",
    "django_htmx",
    "debug_toolbar",
    "constance",
    "user.apps.UserConfig",
    "bookmarks.apps.BookmarksConfig",
    "home.apps.HomeConfig",
    "applications.apps.ApplicationsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "MiCasa.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "home.context_processors.dynamic_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "MiCasa.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": env.db(),
}

# Logging config
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "user.User"

# Storage
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = env("TIMEZONE")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # Used by whitenoise

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Constance dynamic settings
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_ADDITIONAL_FIELDS = {
    "temperature": [
        "django.forms.fields.ChoiceField",
        {"widget": "django.forms.Select", "choices": (("celsius", "Celsius"), ("farenheit", "Farenheit"))},
    ],
    "extra": [
        "django.forms.fields.ChoiceField",
        {"widget": "django.forms.Select", "choices": (("cloud", "Cloud coverage"), ("humidity", "Humidity"))},
    ],
}
CONSTANCE_CONFIG = {
    "WEATHERAPI_KEY": ("", "API Key for weather API"),
    "WEATHERAPI_LAT": (0.0, "Latitude", float),
    "WEATHERAPI_LON": (0.0, "Latitude", float),
    "WEATHERAPI_TEMP": ("celsius", "Temperature format", "temperature"),
    "WEATHERAPI_COVERAGE": ("cloud", "Additional weather data", "extra"),
    "PAGE_TITLE": ("MiCasa", "Page title", str),
}
