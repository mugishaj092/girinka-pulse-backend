from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DistrictViewSet

router = DefaultRouter()
router.register("", DistrictViewSet, basename="districts")
urlpatterns = [path("", include(router.urls))]
