
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MilkProductionViewSet

router = DefaultRouter()
router.register("", MilkProductionViewSet, basename="milk")
urlpatterns = [path("", include(router.urls))]
