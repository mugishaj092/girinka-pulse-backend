from .base import *  # noqa
import sentry_sdk
from decouple import config

DEBUG = False

# Allow Render domains
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default=".onrender.com", cast=Csv())

SECURE_HSTS_SECONDS            = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT            = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SECURE_BROWSER_XSS_FILTER      = True
SECURE_CONTENT_TYPE_NOSNIFF    = True
X_FRAME_OPTIONS                = "DENY"
SECURE_PROXY_SSL_HEADER        = ("HTTP_X_FORWARDED_PROTO", "https")

# Production cache — still in-memory per process (upgrade to memcached if needed)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "girinka-prod-cache",
    }
}

sentry_sdk.init(
    dsn=config("SENTRY_DSN", default=""),
    traces_sample_rate=0.1,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
