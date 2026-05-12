from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from shared.permissions import IsAdmin, IsCellLeaderOrAbove
from .models import District
from .serializers import DistrictSerializer


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdmin()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=["🗺️ Districts"],
        summary="List all districts",
        description="Returns all 30 Rwanda districts with GPS coordinates and remote area flags.",
        responses={200: DistrictSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🗺️ Districts"],
        summary="Create a district",
        description="Register a new district. Admin only.",
        request=DistrictSerializer,
        responses={201: DistrictSerializer},
        examples=[OpenApiExample(
            "New district",
            value={
                "district_name": "Nyarugenge",
                "province": "Kigali",
                "sector": "Nyamirambo",
                "cell": "Cyimana",
                "latitude": -1.9500,
                "longitude": 30.0588,
                "is_remote": False,
            },
            request_only=True,
        )],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["🗺️ Districts"],
        summary="Get district details",
        description="Full district record including province, GPS, and remote flag.",
        responses={200: DistrictSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🗺️ Districts"],
        summary="Update a district",
        description="Partially or fully update a district record. Admin only.",
        request=DistrictSerializer,
        responses={200: DistrictSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["🗺️ Districts"],
        summary="District live statistics",
        description=(
            "Returns cached district statistics (TTL 1 hour):\n"
            "- Total living cows\n"
            "- At-risk cows (AT_RISK, HIGH_RISK, CRITICAL, EMERGENCY)\n"
            "- Average daily milk yield\n"
            "- Total active beneficiaries"
        ),
        responses={
            200: OpenApiResponse(
                description="District statistics",
                examples=[OpenApiExample(
                    "Gasabo stats",
                    value={
                        "total_cows": 1240,
                        "at_risk_cows": 87,
                        "avg_milk": 11.3,
                        "total_beneficiaries": 980,
                    },
                )],
            )
        },
    )
    @action(detail=True, methods=["get"], permission_classes=[IsCellLeaderOrAbove])
    def stats(self, request, pk=None):
        district = self.get_object()
        cache_key = f"district_stats_{district.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        stats = district.get_stats()
        cache.set(cache_key, stats, 3600)
        return Response(stats)

    @extend_schema(
        tags=["🗺️ Districts"],
        summary="Latest weather for this district",
        description="Returns the most recent weather reading (temperature °C, rainfall mm, humidity %) for the district.",
        responses={
            200: OpenApiResponse(
                description="Latest weather reading",
                examples=[OpenApiExample(
                    "Gasabo weather",
                    value={
                        "id": 145,
                        "district": 3,
                        "district_name": "Gasabo",
                        "temperature": 21.4,
                        "humidity": 72.0,
                        "rainfall": 2.5,
                        "wind_speed": 8.0,
                        "reading_time": "2026-05-02T05:00:00+02:00",
                        "data_source": "OpenMeteo",
                        "forecast_day": 0,
                    },
                )],
            )
        },
    )
    @action(detail=True, methods=["get"])
    def weather(self, request, pk=None):
        district = self.get_object()
        weather = district.get_latest_weather()
        if not weather:
            return Response({"detail": "No weather data available."})
        from features.weather.serializers import WeatherDataSerializer
        return Response(WeatherDataSerializer(weather).data)
