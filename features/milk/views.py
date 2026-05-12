from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Sum
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .models import MilkProduction
from .serializers import MilkProductionSerializer
from features.cows.models import Cow


class MilkProductionViewSet(viewsets.ModelViewSet):
    queryset = MilkProduction.objects.select_related("cow").all()
    serializer_class = MilkProductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "FARMER":
            return qs.filter(cow__beneficiary__user=user)
        if user.role in ("CELL_LEADER", "VETERINARIAN", "DISTRICT_LEADER"):
            return qs.filter(cow__district=user.district)
        return qs

    @extend_schema(
        tags=["🥛 Milk Production"],
        summary="List milk records",
        description="Returns daily milk production records filtered by role scope.",
        responses={200: MilkProductionSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs): return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🥛 Milk Production"],
        summary="Log daily milk production",
        description=(
            "Record a cow's daily milk yield. "
            "`daily_yield` must equal `morning_yield + evening_yield` (within 0.5L tolerance)."
        ),
        request=MilkProductionSerializer,
        responses={201: MilkProductionSerializer},
        examples=[
            OpenApiExample(
                "Full record — good yield",
                value={
                    "cow": 42, "collection_date": "2026-05-02",
                    "morning_yield": 6.8, "evening_yield": 5.7,
                    "daily_yield": 12.5, "feed_amount": 6.0,
                    "water_intake": 35.0,
                    "notes": "Cow looked healthy and calm during milking.",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Reduced yield — Ankole cow",
                value={
                    "cow": 18, "collection_date": "2026-05-02",
                    "morning_yield": 2.9, "evening_yield": 2.6,
                    "daily_yield": 5.5, "feed_amount": 4.0, "water_intake": 25.0,
                },
                request_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs): return super().create(request, *args, **kwargs)

    @extend_schema(tags=["🥛 Milk Production"], summary="Get milk record detail")
    def retrieve(self, request, *args, **kwargs): return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🥛 Milk Production"],
        summary="Update a milk record",
        description="Correct a mistakenly entered yield value.",
        request=MilkProductionSerializer,
        responses={200: MilkProductionSerializer},
    )
    def partial_update(self, request, *args, **kwargs): return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["🥛 Milk Production"],
        summary="Run 7-day milk forecast",
        description="Triggers the LSTM forecast for a cow. Requires `?cow_id=` query parameter and ≥7 days of records.",
        parameters=[OpenApiParameter("cow_id", OpenApiTypes.INT, description="ID of the cow to forecast", required=True)],
        responses={
            200: OpenApiResponse(description="7-day forecast"),
            400: OpenApiResponse(description="cow_id not provided"),
            422: OpenApiResponse(description="INSUFFICIENT_MILK_DATA"),
        },
    )
    @action(detail=False, methods=["get"])
    def forecast(self, request):
        cow_id = request.query_params.get("cow_id")
        if not cow_id:
            return Response({"detail": "cow_id required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cow = Cow.objects.get(id=cow_id)
        except Cow.DoesNotExist:
            return Response({"detail": "Cow not found."}, status=status.HTTP_404_NOT_FOUND)
        from features.predictions.services import PredictionService
        result = PredictionService.run_milk_forecast(cow)
        return Response(result)

    @extend_schema(
        tags=["🥛 Milk Production"],
        summary="Production summary",
        description="Returns aggregate stats: total records, average daily yield, and total litres for the user's scope.",
        responses={
            200: OpenApiResponse(
                description="Summary stats",
                examples=[OpenApiExample(
                    "District summary",
                    value={"total_records": 4820, "avg_daily_yield": 10.74, "total_yield": 51765.8},
                )],
            )
        },
    )
    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        return Response({
            "total_records":   qs.count(),
            "avg_daily_yield": round(qs.aggregate(avg=Avg("daily_yield"))["avg"] or 0, 2),
            "total_yield":     round(qs.aggregate(total=Sum("daily_yield"))["total"] or 0, 2),
        })
