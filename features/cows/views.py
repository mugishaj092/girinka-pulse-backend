from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import (
    extend_schema, OpenApiExample, OpenApiParameter,
    OpenApiResponse, inline_serializer
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers as s

from shared.permissions import IsCellLeaderOrAbove, IsAdmin
from .models import Cow
from .serializers import CowSerializer, CowCreateSerializer, CowDeathSerializer
from .filters import CowFilter


class CowViewSet(viewsets.ModelViewSet):
    queryset = Cow.objects.select_related("beneficiary", "district").all()
    filter_backends   = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class   = CowFilter
    search_fields     = ["tag_number", "breed", "beneficiary__full_name"]
    ordering_fields   = ["created_at", "mortality_risk_score", "health_status"]

    def get_serializer_class(self):
        if self.action == "create":
            return CowCreateSerializer
        return CowSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsCellLeaderOrAbove()]
        if self.action in ("update", "partial_update", "death"):
            return [IsCellLeaderOrAbove()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "FARMER":
            return qs.filter(beneficiary__user=user)
        if user.role in ("CELL_LEADER", "VETERINARIAN", "DISTRICT_LEADER"):
            return qs.filter(district=user.district)
        return qs

    # ─────────────────────────────────────────────────────────────────────────
    @extend_schema(
        tags=["🐮 Cows"],
        summary="List cows",
        description=(
            "Returns cows filtered by role:\n"
            "- **Farmer** → own cows only\n"
            "- **Cell Leader / Vet** → all cows in their district\n"
            "- **District Leader / Admin** → all cows nationally\n\n"
            "Supports filtering by `breed`, `health_status`, `is_alive`, `district`, and risk score range."
        ),
        parameters=[
            OpenApiParameter("breed",          OpenApiTypes.STR,  description="Filter by breed e.g. FRIESIAN_CROSS"),
            OpenApiParameter("health_status",  OpenApiTypes.STR,  description="Filter by health status e.g. HIGH_RISK"),
            OpenApiParameter("is_alive",       OpenApiTypes.BOOL, description="true = living cows only"),
            OpenApiParameter("risk_min",       OpenApiTypes.FLOAT,description="Min mortality risk score (0.0–1.0)"),
            OpenApiParameter("risk_max",       OpenApiTypes.FLOAT,description="Max mortality risk score (0.0–1.0)"),
            OpenApiParameter("search",         OpenApiTypes.STR,  description="Search by tag number or farmer name"),
            OpenApiParameter("ordering",       OpenApiTypes.STR,  description="Sort: created_at, mortality_risk_score, health_status"),
        ],
        responses={200: CowSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Register a new cow",
        description=(
            "Register a new cow and assign it to a beneficiary. "
            "Tag number must be unique. Cell Leader or Admin only."
        ),
        request=CowCreateSerializer,
        responses={201: CowSerializer},
        examples=[
            OpenApiExample(
                "Friesian cow — Gasabo",
                value={
                    "tag_number": "RW-GAS-2026-001",
                    "breed": "FRIESIAN_CROSS",
                    "dob": "2022-03-15",
                    "beneficiary": 12,
                    "district": 3,
                    "origin_type": "DIRECT_PROGRAM",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Ankole cow — Bugesera",
                value={
                    "tag_number": "RW-BUG-2026-047",
                    "breed": "ANKOLE",
                    "dob": "2021-11-20",
                    "beneficiary": 38,
                    "district": 7,
                    "origin_type": "BORN_ON_FARM",
                },
                request_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Get cow profile",
        description=(
            "Full cow profile including breed, health status, mortality risk score, "
            "lactation number, days in milk, and owner details."
        ),
        responses={
            200: OpenApiResponse(
                description="Cow profile",
                examples=[OpenApiExample(
                    "Healthy Friesian cow",
                    value={
                        "id": 42,
                        "tag_number": "RW-GAS-2026-001",
                        "breed": "FRIESIAN_CROSS",
                        "dob": "2022-03-15",
                        "age_months": 50,
                        "health_status": "HEALTHY",
                        "mortality_risk_score": 0.12,
                        "is_alive": True,
                        "lactation_number": 2,
                        "days_in_milk": 95,
                        "beneficiary": 12,
                        "beneficiary_name": "Jean Baptiste Nzeyimana",
                        "district": 3,
                        "district_name": "Gasabo",
                    },
                )],
            )
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Update cow details",
        description="Update breed, lactation number, or days in milk. Cell Leader, Vet, or Admin only.",
        request=CowSerializer,
        responses={200: CowSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Record cow death",
        description=(
            "Mark a cow as deceased. Sets `is_alive=false`, `health_status=DECEASED`, "
            "records the date and cause. **Irreversible.** Cell Leader, Vet, or Admin only."
        ),
        request=inline_serializer("CowDeathRequest", fields={"cause": s.CharField()}),
        responses={
            200: OpenApiResponse(
                description="Death recorded",
                examples=[OpenApiExample(
                    "Respiratory illness",
                    value={
                        "id": 42, "tag_number": "RW-GAS-2026-001",
                        "is_alive": False, "health_status": "DECEASED",
                        "death_date": "2026-05-02", "death_cause": "Severe respiratory illness",
                    },
                )],
            ),
            422: OpenApiResponse(description="COW_ALREADY_DECEASED — cow is already dead"),
        },
        examples=[
            OpenApiExample("Respiratory illness", value={"cause": "Severe respiratory illness"}, request_only=True),
            OpenApiExample("Accident",            value={"cause": "Fell into ditch — broken leg"}, request_only=True),
        ],
    )
    @action(detail=True, methods=["post"])
    def death(self, request, pk=None):
        cow = self.get_object()
        serializer = CowDeathSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cow.record_death(serializer.validated_data["cause"], request.user)
        return Response(CowSerializer(cow).data)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Upload cow photo",
        description=(
            "Upload a photo of the cow. Image is stored on **Cloudinary** under `girinka/cows/` "
            "and automatically resized to 800×600. Returns the public Cloudinary URL."
        ),
        request=inline_serializer("CowPhotoRequest", fields={"photo": s.ImageField()}),
        responses={
            200: OpenApiResponse(
                description="Photo uploaded",
                examples=[OpenApiExample(
                    "Upload success",
                    value={"photo_url": "https://res.cloudinary.com/dhforyx1s/image/upload/girinka/cows/cow_RW-GAS-2026-001.jpg"},
                )],
            )
        },
    )
    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser])
    def upload_photo(self, request, pk=None):
        cow   = self.get_object()
        photo = request.FILES.get("photo")
        if not photo:
            return Response({"detail": "No photo provided."}, status=status.HTTP_400_BAD_REQUEST)
        from shared.cloudinary_utils import upload_cow_photo
        url = upload_cow_photo(photo, cow.tag_number)
        if not url:
            return Response({"detail": "Upload failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"photo_url": url})

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Get health records",
        description="Returns the last 20 veterinary health records for this cow, newest first.",
    )
    @action(detail=True, methods=["get"])
    def health(self, request, pk=None):
        cow = self.get_object()
        from features.health.serializers import HealthRecordSerializer
        records = cow.health_records.order_by("-date_recorded")[:20]
        return Response(HealthRecordSerializer(records, many=True).data)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Get milk production history",
        description="Returns the last 30 daily milk production records for this cow.",
    )
    @action(detail=True, methods=["get"])
    def milk(self, request, pk=None):
        cow = self.get_object()
        from features.milk.serializers import MilkProductionSerializer
        records = cow.milk_records.order_by("-collection_date")[:30]
        return Response(MilkProductionSerializer(records, many=True).data)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Get active alerts",
        description="Returns all unresolved AI alerts for this cow.",
    )
    @action(detail=True, methods=["get"])
    def alerts(self, request, pk=None):
        cow = self.get_object()
        from features.alerts.serializers import AlertSerializer
        alerts = cow.alerts.filter(is_resolved=False).order_by("-alert_timestamp")[:20]
        return Response(AlertSerializer(alerts, many=True).data)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Get lineage tree",
        description="Returns the cow's lineage record including mother, generation number, birth weight, and birth health.",
    )
    @action(detail=True, methods=["get"])
    def lineage(self, request, pk=None):
        cow = self.get_object()
        from features.lineage.serializers import LineageSerializer
        try:
            return Response(LineageSerializer(cow.lineage).data)
        except Exception:
            return Response({"detail": "No lineage record found."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Get prediction history",
        description="Returns the last 20 AI prediction logs for this cow (mortality, milk, disease, birth).",
    )
    @action(detail=True, methods=["get"])
    def predictions(self, request, pk=None):
        cow = self.get_object()
        from features.predictions.serializers import PredictionLogSerializer
        logs = cow.predictions.order_by("-predicted_at")[:20]
        return Response(PredictionLogSerializer(logs, many=True).data)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Run mortality risk prediction",
        description=(
            "Triggers a live **CatBoost** mortality risk prediction for this cow. "
            "Updates `mortality_risk_score` and `health_status`. "
            "Creates an alert if risk ≥ 0.50. Sends email if risk ≥ 0.60."
        ),
        request=None,
        responses={
            200: OpenApiResponse(
                description="Prediction result",
                examples=[OpenApiExample(
                    "High risk cow",
                    value={
                        "mortality_risk_score": 0.7155,
                        "risk_level": "HIGH",
                        "alert_triggered": True,
                        "alert_severity": "URGENT",
                        "recommended_action": "🔶 Urgent vet consultation within 24 hours.",
                        "model_version": "v1.0.0",
                    },
                )],
            )
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsCellLeaderOrAbove])
    def predict_risk(self, request, pk=None):
        from features.predictions.services import PredictionService
        cow = self.get_object()
        result = PredictionService.run_mortality_check(cow)
        return Response(result)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="Run milk yield forecast",
        description=(
            "Triggers a live **LSTM** 7-day milk forecast. "
            "Requires at least 7 days of milk records. Returns daily predictions and average."
        ),
        request=None,
        responses={
            200: OpenApiResponse(
                description="7-day milk forecast",
                examples=[OpenApiExample(
                    "Forecast result",
                    value={
                        "forecast_days": 7,
                        "forecasts": [
                            {"day": 1, "predicted_yield_litres": 12.3, "confidence": "high"},
                            {"day": 2, "predicted_yield_litres": 12.1, "confidence": "high"},
                            {"day": 3, "predicted_yield_litres": 11.9, "confidence": "high"},
                        ],
                        "avg_predicted_yield_litres": 12.1,
                        "total_predicted_litres": 84.7,
                        "data_quality": "sufficient",
                    },
                )],
            ),
            422: OpenApiResponse(description="INSUFFICIENT_MILK_DATA — need 7+ days of records"),
        },
    )
    @action(detail=True, methods=["post"])
    def predict_milk(self, request, pk=None):
        from features.predictions.services import PredictionService
        cow = self.get_object()
        result = PredictionService.run_milk_forecast(cow)
        return Response(result)

    @extend_schema(
        tags=["🐮 Cows"],
        summary="List at-risk cows",
        description=(
            "Returns all living cows with `health_status` in `AT_RISK`, `HIGH_RISK`, `CRITICAL`, or `EMERGENCY`, "
            "sorted by `mortality_risk_score` descending. Cell Leader, Vet, or Admin only."
        ),
        responses={200: CowSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsCellLeaderOrAbove])
    def at_risk(self, request):
        qs = self.get_queryset().filter(
            health_status__in=["AT_RISK", "HIGH_RISK", "CRITICAL", "EMERGENCY"],
            is_alive=True,
        ).order_by("-mortality_risk_score")
        page       = self.paginate_queryset(qs)
        serializer = CowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
