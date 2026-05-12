
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LineageViewSet
router = DefaultRouter()
router.register("", LineageViewSet, basename="lineage")
urlpatterns = [path("", include(router.urls))]
