from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import serializers as s

from shared.permissions import IsCellLeaderOrAbove
from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related("cow", "beneficiary", "model").all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "FARMER":
            return qs.filter(beneficiary__user=user)
        if user.role in ("CELL_LEADER", "VETERINARIAN", "DISTRICT_LEADER"):
            return qs.filter(cow__district=user.district)
        return qs

    @extend_schema(
        tags=["🚨 Alerts"],
        summary="List alerts",
        description=(
            "Returns alerts scoped to the user's role:\n"
            "- **Farmer** → alerts for own cows\n"
            "- **Cell Leader / Vet** → all alerts in their district\n"
            "- **Admin** → all alerts nationally\n\n"
            "Filter by `?is_resolved=false` to see only active alerts."
        ),
        responses={200: AlertSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🚨 Alerts"],
        summary="Get alert details",
        description="Full alert record including risk score, recommendation, SMS status, and resolution history.",
        responses={
            200: OpenApiResponse(
                description="Alert detail",
                examples=[OpenApiExample(
                    "Urgent mortality alert",
                    value={
                        "id": 87, "alert_type": "MORTALITY_RISK", "severity": "URGENT",
                        "risk_score": 0.72,
                        "message": "Mortality risk score: 0.72 — HIGH",
                        "recommendation": "🔶 Urgent vet consultation within 24 hours. Monitor closely.",
                        "cow": 42, "cow_tag": "RW-GAS-2026-001",
                        "beneficiary_name": "Uwimana Claudine",
                        "is_resolved": False, "sent_via_sms": False,
                        "alert_timestamp": "2026-05-02T06:30:00+02:00",
                    },
                )],
            )
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🚨 Alerts"],
        summary="Resolve an alert",
        description=(
            "Mark an alert as resolved. Records who resolved it, when, and optional notes. "
            "Cell Leader, Vet, or Admin only."
        ),
        request=inline_serializer("ResolveRequest", fields={"notes": s.CharField(required=False, allow_blank=True)}),
        responses={
            200: OpenApiResponse(
                description="Alert resolved",
                examples=[OpenApiExample(
                    "Resolved",
                    value={"id": 87, "is_resolved": True, "resolved_at": "2026-05-02T09:15:00+02:00", "resolution_notes": "Vet visited. Cow given antibiotics. Risk reduced."},
                )],
            )
        },
        examples=[
            OpenApiExample("Vet visited",       value={"notes": "Vet visited on 02/05. Cow given antibiotics. Risk reduced."}, request_only=True),
            OpenApiExample("No action needed",  value={"notes": "Monitored for 48h. Cow stable. No treatment needed."}, request_only=True),
        ],
    )
    @action(detail=True, methods=["post"], permission_classes=[IsCellLeaderOrAbove])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.is_resolved     = True
        alert.resolved_at     = timezone.now()
        alert.resolved_by     = request.user
        alert.resolution_notes = request.data.get("notes", "")
        alert.save(update_fields=["is_resolved", "resolved_at", "resolved_by", "resolution_notes"])
        
        # Create in-app notification for farmer
        from features.notifications.models import Notification
        if alert.beneficiary.user:
            Notification.objects.create(
                user=alert.beneficiary.user,
                alert=alert,
                title=f"✅ Alert Resolved: {alert.alert_type.replace('_', ' ').title()}",
                message=f"Your alert for cow {alert.cow.tag_number} has been resolved by {request.user.full_name}. Notes: {alert.resolution_notes or 'No additional notes.'}",
            )
        
        return Response(AlertSerializer(alert).data)

    @extend_schema(
        tags=["🚨 Alerts"],
        summary="Escalate alert severity",
        description=(
            "Escalate the severity one level up:\n"
            "`INFO` → `WARNING` → `URGENT` → `CRITICAL`\n\n"
            "Already CRITICAL alerts are not changed further."
        ),
        request=None,
        responses={
            200: OpenApiResponse(
                description="Severity escalated",
                examples=[OpenApiExample("Escalated", value={"id": 87, "severity": "CRITICAL"})],
            )
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsCellLeaderOrAbove])
    def escalate(self, request, pk=None):
        alert = self.get_object()
        from .models import AlertSeverity
        escalation_map = {
            AlertSeverity.INFO:    AlertSeverity.WARNING,
            AlertSeverity.WARNING: AlertSeverity.URGENT,
            AlertSeverity.URGENT:  AlertSeverity.CRITICAL,
        }
        alert.severity = escalation_map.get(alert.severity, alert.severity)
        alert.save(update_fields=["severity"])
        return Response(AlertSerializer(alert).data)

    @extend_schema(
        tags=["🚨 Alerts"],
        summary="Count unresolved alerts",
        description="Returns the count of unresolved alerts in the current user's scope. Useful for notification badges.",
        responses={
            200: OpenApiResponse(
                description="Unread count",
                examples=[OpenApiExample("Count", value={"unread_count": 14})],
            )
        },
    )
    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_resolved=False).count()
        return Response({"unread_count": count})

    @extend_schema(
        tags=["🚨 Alerts"],
        summary="Bulk resolve alerts",
        description="Resolve multiple alerts at once by providing a list of alert IDs. Admin only.",
        request=inline_serializer("BulkResolveRequest", fields={"alert_ids": s.ListField(child=s.IntegerField())}),
        responses={200: OpenApiResponse(description="Number of alerts resolved", examples=[OpenApiExample("Resolved", value={"resolved": 5})])},
        examples=[OpenApiExample("Bulk resolve 5 alerts", value={"alert_ids": [1, 3, 7, 12, 18]}, request_only=True)],
    )
    @action(detail=False, methods=["post"], permission_classes=[IsCellLeaderOrAbove])
    def bulk_resolve(self, request):
        ids = request.data.get("alert_ids", [])
        updated = Alert.objects.filter(id__in=ids).update(
            is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user
        )
        return Response({"resolved": updated})
