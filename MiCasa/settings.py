from pathlib import Path
import environ
import os
import logging.config
from django.utils.translation import gettext_lazy as _
from django.utils.log import DEFAULT_LOGGING
from django.contrib.messages import constants as messages


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    DATABASE_URL=(str, "sqlite:////data/micasa.db"),
    CACHE_URL=(str, "filecache:///var/tmp/django_cache"),
    TIMEZONE=(str, "Europe/Paris"),
    APP_URL=(str, None),
    OIDC_ENABLED=(bool, False),
    OIDC_CLIENT_ID=(str, None),
    OIDC_CLIENT_SECRET=(str, None),
    OIDC_AUTH_ENDPOINT=(str, None),
    OIDC_TOKEN_ENDPOINT=(str, None),
    OIDC_USER_ENDPOINT=(str, None),
    OIDC_SIGN_ALGO=(str, "HS256"),
    OIDC_JWKS_ENDPOINT=(str, None),
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
    "dynamic_preferences",
    "user.apps.UserConfig",
    "bookmarks.apps.BookmarksConfig",
    "home.apps.HomeConfig",
    "applications.apps.ApplicationsConfig",
    "mozilla_django_oidc",
    "health_check",
    "health_check.db",
    # "health_check.cache",
    "health_check.contrib.migrations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
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
                "dynamic_preferences.processors.global_preferences",
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

# Caching support
CACHES = {"default": env.cache()}

# Logging config
LOGGING_CONFIG = None
LOGLEVEL = env("LOGLEVEL", default="info").upper()

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                # exact format is not important, this is the minimum information
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            },
            "django.server": DEFAULT_LOGGING["formatters"]["django.server"],
        },
        "handlers": {
            # console logs to stderr
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "django.server": DEFAULT_LOGGING["handlers"]["django.server"],
        },
        "loggers": {
            # default for all undefined Python modules
            "": {
                "level": "WARNING",
                "handlers": ["console"],
            },
            # Our application code
            "applications": {
                "level": LOGLEVEL,
                "handlers": ["console"],
                # Avoid double logging because of root logger
                "propagate": False,
            },
            "user": {
                "level": LOGLEVEL,
                "handlers": ["console"],
                # Avoid double logging because of root logger
                "propagate": False,
            },
            # Default runserver request logging
            "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
        },
    }
)

AUTHENTICATION_BACKENDS = (
    "mozilla_django_oidc.auth.OIDCAuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
    # ...
)

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

# Default auth routes
LOGIN_URL = "user:login"
LOGIN_REDIRECT_URL = "user:index"
LOGOUT_REDIRECT_URL = "home:index"

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

LANGUAGES = (
    ("en-us", _("English")),
    ("fr-fr", _("French")),
)

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

TIME_ZONE = env("TIMEZONE")

USE_I18N = True
USE_L10N = True

USE_TZ = True


# Messages : mapping level to halfmoon classes for alerts
MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
    messages.INFO: "alert-info",
}

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

# Dynamic preferences package
DYNAMIC_PREFERENCES = {"ENABLE_CACHE": not env("DEBUG"), "REGISTRY_MODULE": "preferences"}


# OIDC configuration
OIDC_ENABLED = env("OIDC_ENABLED")
OIDC_RP_CLIENT_ID = env("OIDC_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = env("OIDC_CLIENT_SECRET")
OIDC_OP_AUTHORIZATION_ENDPOINT = env("OIDC_AUTH_ENDPOINT")
OIDC_OP_TOKEN_ENDPOINT = env("OIDC_TOKEN_ENDPOINT")
OIDC_OP_USER_ENDPOINT = env("OIDC_USER_ENDPOINT")
OIDC_RP_SIGN_ALGO = env("OIDC_SIGN_ALGO")
OIDC_OP_JWKS_ENDPOINT = env("OIDC_JWKS_ENDPOINT")
