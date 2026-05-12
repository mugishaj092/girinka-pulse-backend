"""Girinka Pulse — Root URL Configuration."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

API_PREFIX = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{API_PREFIX}schema/", SpectacularAPIView.as_view(), name="schema"),
    path(f"{API_PREFIX}docs/", SpectacularSwaggerView.as_view(url_name="schema", template_name="swagger-ui.html"), name="swagger-ui"),
    path(f"{API_PREFIX}redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path(f"{API_PREFIX}auth/",          include("features.auth.urls")),
    path(f"{API_PREFIX}users/",         include("features.users.urls")),
    path(f"{API_PREFIX}districts/",     include("features.districts.urls")),
    path(f"{API_PREFIX}beneficiaries/", include("features.beneficiaries.urls")),
    path(f"{API_PREFIX}cows/",          include("features.cows.urls")),
    path(f"{API_PREFIX}health/",        include("features.health.urls")),
    path(f"{API_PREFIX}milk/",          include("features.milk.urls")),
    path(f"{API_PREFIX}alerts/",        include("features.alerts.urls")),
    path(f"{API_PREFIX}predictions/",   include("features.predictions.urls")),
    path(f"{API_PREFIX}passon/",        include("features.passon.urls")),
    path(f"{API_PREFIX}lineage/",       include("features.lineage.urls")),
    path(f"{API_PREFIX}reports/",       include("features.reports.urls")),
    path(f"{API_PREFIX}weather/",       include("features.weather.urls")),
    path(f"{API_PREFIX}notifications/", include("features.notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
