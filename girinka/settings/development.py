from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} — {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
    "loggers": {
        "django.db.backends": {"handlers": ["console"], "level": "INFO"},
        "celery":             {"handlers": ["console"], "level": "INFO"},
        "girinka":            {"handlers": ["console"], "level": "DEBUG"},
        "features":           {"handlers": ["console"], "level": "DEBUG"},
    },
}
