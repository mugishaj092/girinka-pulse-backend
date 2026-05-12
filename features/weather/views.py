
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import WeatherData
from .serializers import WeatherDataSerializer


class WeatherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeatherData.objects.select_related("district").all()
    serializer_class = WeatherDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        district_id = self.request.query_params.get("district_id")
        if district_id:
            qs = qs.filter(district_id=district_id)
        return qs.order_by("-reading_time")[:200]

    @extend_schema(
        tags=["🌤️ Weather"],
        summary="List weather readings",
        description=(
            "Returns recent weather readings for all districts. "
            "Auto-fetched daily at 05:00 AM from Open-Meteo.\n\n"
            "Filter by `district_id` to see readings for a specific district."
        ),
        parameters=[
            OpenApiParameter("district_id", OpenApiTypes.INT, description="Filter by district ID"),
        ],
        responses={200: WeatherDataSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🌤️ Weather"],
        summary="Get weather reading",
        description="Returns a single weather data reading.",
        responses={200: WeatherDataSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🌤️ Weather"],
        summary="7-day weather forecast",
        description=(
            "Returns the 7-day weather forecast for a district. "
            "Data is sourced from Open-Meteo and stored daily."
        ),
        parameters=[
            OpenApiParameter("district_id", OpenApiTypes.INT, description="District ID to forecast"),
        ],
        responses={
            200: OpenApiResponse(
                description="7-day forecast",
                examples=[
                    OpenApiExample(
                        "Gasabo forecast",
                        value={
                            "success": True,
                            "data": [
                                {
                                    "district": 3,
                                    "district_name": "Gasabo",
                                    "forecast_day": 1,
                                    "temperature": 22.1,
                                    "rainfall": 0.0,
                                    "humidity": 68.0,
                                    "reading_time": "2026-05-03T05:00:00+02:00",
                                }
                            ],
                        },
                    )
                ],
            )
        },
    )
    @action(detail=False, methods=["get"])
    def forecast(self, request):
        district_id = request.query_params.get("district_id")
        qs = WeatherData.objects.filter(forecast_day__gt=0)
        if district_id:
            qs = qs.filter(district_id=district_id)
        return Response(WeatherDataSerializer(qs.order_by("forecast_day")[:7], many=True).data)
