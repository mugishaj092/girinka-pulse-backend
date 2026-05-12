
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CowViewSet

router = DefaultRouter()
router.register("", CowViewSet, basename="cows")
urlpatterns = [path("", include(router.urls))]
