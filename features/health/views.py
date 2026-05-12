
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from shared.permissions import IsVetOrAbove, IsCellLeaderOrAbove
from .models import Veterinarian, HealthRecord
from .serializers import VeterinarianSerializer, HealthRecordSerializer


class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.select_related("cow", "vet").all()
    serializer_class = HealthRecordSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "schedule"):
            return [IsVetOrAbove()]
        return [IsCellLeaderOrAbove()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role in ("CELL_LEADER", "VETERINARIAN", "DISTRICT_LEADER"):
            return qs.filter(cow__district=user.district)
        return qs

    @extend_schema(
        tags=["🩺 Health Records"],
        summary="List health records",
        description=(
            "Returns veterinary health records filtered by district for Cell Leaders and Vets.\n\n"
            "Filter by `cow`, `vet`, `date_after`, `date_before`."
        ),
        responses={200: HealthRecordSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🩺 Health Records"],
        summary="Create a health record",
        description="Record a new veterinary visit for a cow. **Veterinarian or Admin only.**",
        request=HealthRecordSerializer,
        responses={
            201: HealthRecordSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "Respiratory infection visit",
                value={
                    "cow": 42,
                    "vet": 5,
                    "diagnosis": "Mild respiratory infection",
                    "treatment_given": "Oxytetracycline 20mg/kg IM injection",
                    "symptoms": "Nasal discharge, mild fever, reduced appetite",
                    "temperature": 39.8,
                    "weight": 380.5,
                    "next_visit_date": "2026-05-16",
                    "date_recorded": "2026-05-02T10:30:00+02:00",
                },
                request_only=True,
            )
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["🩺 Health Records"],
        summary="Get health record",
        description="Returns full details of a single veterinary health record.",
        responses={200: HealthRecordSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🩺 Health Records"],
        summary="Update health record",
        description="Update a health record — add treatment notes or reschedule next visit. **Vet or Admin only.**",
        request=HealthRecordSerializer,
        responses={200: HealthRecordSerializer},
        examples=[
            OpenApiExample(
                "Add follow-up treatment",
                value={
                    "treatment_given": "Oxytetracycline 20mg/kg IM. Follow-up with vitamins.",
                    "next_visit_date": "2026-05-20",
                },
                request_only=True,
            )
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["🩺 Health Records"],
        summary="List upcoming vet visits",
        description="Returns all upcoming scheduled vet visits ordered by date.",
        responses={200: HealthRecordSerializer(many=True)},
        methods=["GET"],
    )
    @extend_schema(
        tags=["🩺 Health Records"],
        summary="Schedule a vet visit",
        description=(
            "Create a new scheduled vet visit for a cow. **Vet or Admin only.**\n\n"
            "This is the same as creating a health record with a `next_visit_date` set."
        ),
        request=HealthRecordSerializer,
        responses={
            201: HealthRecordSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "Schedule follow-up",
                value={
                    "cow": 42,
                    "vet": 5,
                    "next_visit_date": "2026-05-16",
                    "diagnosis": "Routine follow-up after respiratory treatment",
                    "date_recorded": "2026-05-02T10:30:00+02:00",
                },
                request_only=True,
            )
        ],
        methods=["POST"],
    )
    @action(detail=False, methods=["get", "post"])
    def schedule(self, request):
        if request.method == "POST":
            serializer = HealthRecordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        upcoming = self.get_queryset().filter(
            next_visit_date__gte=timezone.now().date()
        ).order_by("next_visit_date")[:50]
        return Response(HealthRecordSerializer(upcoming, many=True).data)
