
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MortalityPredictionView, MilkPredictionView, DiseasePredictionView,
    BirthPredictionView, PredictionHistoryViewSet, AIModelViewSet
)

router = DefaultRouter()
router.register("history", PredictionHistoryViewSet, basename="prediction-history")
router.register("models",  AIModelViewSet,           basename="ai-models")

urlpatterns = [
    path("mortality/", MortalityPredictionView.as_view()),
    path("milk/",      MilkPredictionView.as_view()),
    path("disease/",   DiseasePredictionView.as_view()),
    path("passon/",    BirthPredictionView.as_view()),
    path("", include(router.urls)),
]
