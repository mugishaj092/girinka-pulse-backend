
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PassOnViewSet

router = DefaultRouter()
router.register("", PassOnViewSet, basename="passon")
urlpatterns = [path("", include(router.urls))]
