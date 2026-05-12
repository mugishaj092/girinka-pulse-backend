"""
Girinka Pulse — Base Settings
No Redis. Uses PostgreSQL for DB + Celery broker.
Cloudinary for file storage. Resend for email.
"""

from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY", default="change-me-in-production")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# ── Application definition ────────────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_extensions",
    "django_celery_beat",
    "django_celery_results",
    "cloudinary",
    "cloudinary_storage",
]

LOCAL_APPS = [
    "features.auth.apps.AuthConfig",
    "features.users.apps.UsersConfig",
    "features.districts.apps.DistrictsConfig",
    "features.beneficiaries.apps.BeneficiariesConfig",
    "features.cows.apps.CowsConfig",
    "features.health.apps.HealthConfig",
    "features.milk.apps.MilkConfig",
    "features.alerts.apps.AlertsConfig",
    "features.predictions.apps.PredictionsConfig",
    "features.passon.apps.PassonConfig",
    "features.lineage.apps.LineageConfig",
    "features.reports.apps.ReportsConfig",
    "features.weather.apps.WeatherConfig",
    "features.notifications.apps.NotificationsConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "shared.middleware.RequestLoggingMiddleware",
]

ROOT_URLCONF = "girinka.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "girinka.wsgi.application"

# ── Database (PostgreSQL) ─────────────────────────────────────────────────────
import dj_database_url

DATABASE_URL = config("DATABASE_URL", default=None)

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=60, ssl_require=True)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME":     config("DB_NAME",     default="girinka-pulse-db"),
            "USER":     config("DB_USER",     default="postgres"),
            "PASSWORD": config("DB_PASSWORD", default="password"),
            "HOST":     config("DB_HOST",     default="localhost"),
            "PORT":     config("DB_PORT",     default="5432"),
            "OPTIONS":  {"sslmode": config("DATABASE_SSL", default="prefer")},
            "CONN_MAX_AGE": 60,
        }
    }

# ── NO REDIS — Celery uses PostgreSQL as broker ───────────────────────────────
if DATABASE_URL:
    # Convert DATABASE_URL to Celery broker format
    CELERY_BROKER_URL = DATABASE_URL.replace("postgresql://", "db+postgresql://").replace("postgres://", "db+postgresql://")
else:
    CELERY_BROKER_URL = config(
        "CELERY_BROKER_URL",
        default="db+postgresql://postgres:password@localhost/girinka-pulse-db"
    )
CELERY_RESULT_BACKEND  = "django-db"         # django_celery_results
CELERY_CACHE_BACKEND   = "default"
CELERY_ACCEPT_CONTENT  = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE        = "Africa/Kigali"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BEAT_SCHEDULER  = "django_celery_beat.schedulers:DatabaseScheduler"

# ── Session (uses DB, not cache) ──────────────────────────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# ── Simple in-memory cache (no Redis) ────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "girinka-cache",
    }
}

# ── Authentication ────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── REST Framework ────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "shared.renderers.GirinkaJSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "shared.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "shared.exceptions.girinka_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon":  "100/min",
        "user":  "200/min",
    },
}

# ── JWT ───────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(hours=config("JWT_ACCESS_TOKEN_LIFETIME_HOURS", default=1, cast=int)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7, cast=int)),
    "ROTATE_REFRESH_TOKENS":  True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

# ── Cloudinary (file & image storage) ────────────────────────────────────────
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY":    config("CLOUDINARY_API_KEY",    default=""),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
    "SECURE":     True,
}

import cloudinary
cloudinary.config(
    cloud_name = config("CLOUDINARY_CLOUD_NAME", default=""),
    api_key    = config("CLOUDINARY_API_KEY",    default=""),
    api_secret = config("CLOUDINARY_API_SECRET", default=""),
    secure     = True,
)

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Resend (email) ────────────────────────────────────────────────────────────
RESEND_API_KEY = config("RESEND_API_KEY", default="")
FROM_EMAIL     = config("FROM_EMAIL", default="Girinka Pulse <no-reply@mugishajoseph.me>")

# Keep Django email backend as dummy — all mail goes through Resend SDK
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

# ── ML Service ────────────────────────────────────────────────────────────────
ML_SERVICE_URL     = config("ML_SERVICE_URL", default="http://localhost:8001")
ML_SERVICE_API_KEY = config("ML_SERVICE_API_KEY", default="")
ML_SERVICE_TIMEOUT = 30
USE_MOCK_ML_CLIENT = config("USE_MOCK_ML_CLIENT", default=False, cast=bool)

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Africa/Kigali"
USE_I18N      = True
USE_TZ        = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── API Docs ──────────────────────────────────────────────────────────────────
# ── drf-spectacular — loaded from spectacular_config.py ─────────────────────
from girinka.spectacular_config import SPECTACULAR_SETTINGS  # noqa

# ── Open-Meteo (weather) ──────────────────────────────────────────────────────
OPENMETEO_BASE_URL = config(
    "OPENMETEO_BASE_URL",
    default="https://api.open-meteo.com/v1/forecast"
)
