
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.none()  # Prevent schema generation errors

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    @extend_schema(
        tags=["🔔 Notifications"],
        summary="List notifications",
        description=(
            "Returns all notifications for the currently authenticated user, newest first.\n\n"
            "Filter by `is_read=false` to see only unread notifications."
        ),
        responses={200: NotificationSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🔔 Notifications"],
        summary="Get notification",
        description="Returns the full details of a single notification.",
        responses={200: NotificationSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🔔 Notifications"],
        summary="Mark notification as read",
        description="Marks a single notification as read and records the `read_at` timestamp.",
        request=None,
        responses={
            200: OpenApiResponse(
                description="Notification marked as read",
                examples=[
                    OpenApiExample(
                        "Marked read",
                        value={
                            "success": True,
                            "data": {
                                "id": 55,
                                "is_read": True,
                                "read_at": "2026-05-02T09:00:00+02:00",
                            },
                        },
                    )
                ],
            )
        },
    )
    @action(detail=True, methods=["patch"])
    def read(self, request, pk=None):
        n = self.get_object()
        n.is_read = True
        n.read_at = timezone.now()
        n.save(update_fields=["is_read", "read_at"])
        return Response(NotificationSerializer(n).data)

    @extend_schema(
        tags=["🔔 Notifications"],
        summary="Mark all notifications as read",
        description="Marks all unread notifications for the current user as read at once.",
        request=None,
        responses={
            200: OpenApiResponse(
                description="All notifications marked as read",
                examples=[
                    OpenApiExample(
                        "Bulk marked",
                        value={"success": True, "data": {"marked_read": 8}},
                    )
                ],
            )
        },
    )
    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        updated = Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({"marked_read": updated})

    @extend_schema(
        tags=["🔔 Notifications"],
        summary="Get notification preferences",
        description=(
            "Returns the current user's notification channel and severity preferences. "
            "Use `PATCH` to this endpoint to update preferences."
        ),
        responses={200: NotificationPreferenceSerializer},
        methods=["GET"],
    )
    @extend_schema(
        tags=["🔔 Notifications"],
        summary="Update notification preferences",
        description=(
            "Update which notification channels are enabled and the minimum severity level to notify on.\n\n"
            "**Min severity options:** `INFO` · `WARNING` · `URGENT` · `CRITICAL`"
        ),
        request=NotificationPreferenceSerializer,
        responses={200: NotificationPreferenceSerializer},
        examples=[
            OpenApiExample(
                "Enable email, disable SMS",
                value={"email": True, "sms": False, "in_app": True, "push": False, "min_severity": "WARNING"},
                request_only=True,
            )
        ],
        methods=["PATCH"],
    )
    @action(detail=False, methods=["get", "patch"], url_path="preferences")
    def preferences(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        if request.method == "GET":
            return Response(NotificationPreferenceSerializer(prefs).data)
        s = NotificationPreferenceSerializer(prefs, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)
