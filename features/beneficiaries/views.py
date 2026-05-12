from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import serializers as s

from shared.permissions import IsCellLeaderOrAbove, IsAdmin, IsAuthenticated
from shared.exceptions import PassonPendingError
from .models import Beneficiary
from .serializers import BeneficiarySerializer, BeneficiaryCreateSerializer, DeregisterSerializer


class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.select_related("district", "user").all()

    def get_serializer_class(self):
        if self.action == "create":
            return BeneficiaryCreateSerializer
        return BeneficiarySerializer

    def get_permissions(self):
        if self.action in ("create", "deregister", "update", "partial_update"):
            return [IsCellLeaderOrAbove()]
        if self.action == "reregister":
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "FARMER":
            return qs.filter(user=user)
        if user.role in ("CELL_LEADER", "VETERINARIAN"):
            return qs.filter(district=user.district)
        if user.role == "DISTRICT_LEADER":
            return qs.filter(district=user.district)
        return qs

    @extend_schema(
        tags=["🏠 Beneficiaries"],
        summary="List beneficiaries",
        description=(
            "Returns farmers enrolled in the Girinka program.\n\n"
            "- **Farmer** → own profile only\n"
            "- **Cell Leader / Vet** → all in their district\n"
            "- **Admin** → all nationally"
        ),
        responses={200: BeneficiarySerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🏠 Beneficiaries"],
        summary="Register a new beneficiary",
        description=(
            "Enroll a new farmer in the Girinka program. "
            "**Ubudehe category must be 1 or 2** — the program only targets the poorest households. "
            "Returns `INVALID_UBUDEHE` (400) if category 3 or 4 is submitted."
        ),
        request=BeneficiaryCreateSerializer,
        responses={
            201: BeneficiarySerializer,
            400: OpenApiResponse(description="INVALID_UBUDEHE or validation error"),
            409: OpenApiResponse(description="DUPLICATE_NATIONAL_ID"),
        },
        examples=[
            OpenApiExample(
                "Rural farmer — Bugesera",
                value={
                    "national_id": "1199080123456789",
                    "full_name": "Uwimana Claudine",
                    "ubudehe_category": 1,
                    "district": 7,
                    "phone_number": "+250788901234",
                    "date_of_birth": "1985-06-20",
                    "gender": "FEMALE",
                    "registration_date": "2026-05-02",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Urban farmer — Gasabo",
                value={
                    "national_id": "1199070987654321",
                    "full_name": "Hakizimana Emmanuel",
                    "ubudehe_category": 2,
                    "district": 3,
                    "phone_number": "+250722456789",
                    "registration_date": "2026-05-02",
                },
                request_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["🏠 Beneficiaries"],
        summary="Get beneficiary profile",
        description="Full farmer profile including district, Ubudehe category, active cow count, and ML risk profile.",
        responses={
            200: OpenApiResponse(
                description="Beneficiary profile",
                examples=[OpenApiExample(
                    "Active farmer",
                    value={
                        "id": 12, "national_id": "1199080123456789",
                        "full_name": "Uwimana Claudine",
                        "ubudehe_category": 1, "district": 7,
                        "district_name": "Bugesera",
                        "phone_number": "+250788901234",
                        "ml_risk_profile": "LOW",
                        "is_active": True, "active_cows": 2,
                        "registration_date": "2026-05-02",
                    },
                )],
            )
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🏠 Beneficiaries"],
        summary="Deregister a farmer",
        description=(
            "Remove a farmer from the Girinka program. "
            "**Blocked** if a pass-on transfer is pending (`PASSON_PENDING` error). "
            "Sets `is_active=false` and records the reason and timestamp."
        ),
        request=DeregisterSerializer,
        responses={
            200: OpenApiResponse(description="Deregistered successfully"),
            422: OpenApiResponse(description="PASSON_PENDING — cannot deregister while transfer is pending"),
        },
        examples=[
            OpenApiExample("Farmer relocated", value={"reason": "RELOCATED", "notes": "Moved to Kigali city"}, request_only=True),
            OpenApiExample("Cow died",         value={"reason": "COW_DIED",   "notes": "Cow died of ECF in March 2026"}, request_only=True),
            OpenApiExample("Rule violation",   value={"reason": "RULE_VIOLATION", "notes": "Cow was sold without authorization"}, request_only=True),
        ],
    )
    @action(detail=True, methods=["post"])
    def deregister(self, request, pk=None):
        beneficiary = self.get_object()
        if beneficiary.passon_donations.filter(status="PENDING").exists():
            raise PassonPendingError()
        serializer = DeregisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        beneficiary.is_active      = False
        beneficiary.deregistered_at = timezone.now()
        beneficiary.deregister_reason = serializer.validated_data["reason"]
        beneficiary.deregister_notes  = serializer.validated_data.get("notes", "")
        beneficiary.deregistered_by   = request.user
        beneficiary.save()
        return Response({"detail": "Beneficiary deregistered."})

    @extend_schema(
        tags=["🏠 Beneficiaries"],
        summary="Reregister a deregistered farmer",
        description="Reactivate a previously deregistered farmer. **Admin only.** Clears the deregistration date and reason.",
        request=None,
        responses={200: BeneficiarySerializer},
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def reregister(self, request, pk=None):
        beneficiary = self.get_object()
        beneficiary.is_active        = True
        beneficiary.deregistered_at  = None
        beneficiary.deregister_reason = None
        beneficiary.save(update_fields=["is_active", "deregistered_at", "deregister_reason"])
        return Response(BeneficiarySerializer(beneficiary).data)

    @extend_schema(
        tags=["🏠 Beneficiaries"],
        summary="List beneficiary's cows",
        description="Returns all living cows owned by this beneficiary.",
    )
    @action(detail=True, methods=["get"])
    def cows(self, request, pk=None):
        beneficiary = self.get_object()
        from features.cows.serializers import CowSerializer
        cows = beneficiary.cows.filter(is_alive=True)
        return Response(CowSerializer(cows, many=True).data)

    @extend_schema(
        tags=["🏠 Beneficiaries"],
        summary="List beneficiary's alerts",
        description="Returns all unresolved alerts linked to this beneficiary's cows.",
    )
    @action(detail=True, methods=["get"])
    def alerts(self, request, pk=None):
        beneficiary = self.get_object()
        from features.alerts.serializers import AlertSerializer
        alerts = beneficiary.alerts.filter(is_resolved=False).order_by("-alert_timestamp")[:20]
        return Response(AlertSerializer(alerts, many=True).data)

    @extend_schema(
        tags=["🏠 Beneficiaries"],
        summary="Beneficiary program history",
        description=(
            "Full program history and timeline for this beneficiary including registration date, "
            "deregistration events, and pass-on transfer history. **Cell Leader and above.**"
        ),
        responses={200: BeneficiarySerializer},
    )
    @action(detail=True, methods=["get"], permission_classes=[IsCellLeaderOrAbove])
    def history(self, request, pk=None):
        beneficiary = self.get_object()
        return Response(BeneficiarySerializer(beneficiary).data)

    @extend_schema(
        tags=["🏠 Beneficiaries"],
        summary="Bulk import from CSV",
        description=(
            "Upload a CSV file to bulk-register many farmers at once. "
            "Processed asynchronously via Celery. "
            "**Required CSV columns:** `national_id`, `full_name`, `ubudehe_category`, `district`, `phone_number`"
        ),
        request=inline_serializer("BulkImportRequest", fields={"file": s.FileField()}),
        responses={202: OpenApiResponse(description="Import queued")},
    )
    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser], permission_classes=[IsAdmin])
    def bulk_import(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        from features.beneficiaries.tasks import process_bulk_import
        process_bulk_import.delay(file.read().decode("utf-8"))
        return Response({"detail": "Import queued. You will be notified when complete."}, status=status.HTTP_202_ACCEPTED)
