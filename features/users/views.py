from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from shared.permissions import IsAdmin
from .models import User, AuditLog
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, AuditLogSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("district").all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserSerializer

    @extend_schema(
        tags=["👥 Users"],
        summary="List all users",
        description=(
            "Returns all user accounts in the system. **Admin only.**\n\n"
            "Filter by `role`, `district`, `is_active`. Search by `username` or `full_name`."
        ),
        responses={200: UserSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["👥 Users"],
        summary="Create a user account",
        description="Create a new user account. **Admin only.** Assign a role and district at creation time.",
        request=UserCreateSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description="Validation error"),
            409: OpenApiResponse(description="DUPLICATE_NATIONAL_ID"),
        },
        examples=[
            OpenApiExample(
                "New Cell Leader",
                value={
                    "username": "uwimana_claudine",
                    "password": "SecurePass@2026",
                    "full_name": "UWIMANA Claudine",
                    "email": "claudine@girinka.rw",
                    "phone_number": "+250788901234",
                    "role": "CELL_LEADER",
                    "district": 7,
                    "national_id": "1199080123456789",
                },
                request_only=True,
            )
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["👥 Users"],
        summary="Get user details",
        description="Returns full details of a specific user account. **Admin only.**",
        responses={200: UserSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["👥 Users"],
        summary="Update user account",
        description="Update a user's name, email, role, district, or active status. **Admin only.**",
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        examples=[
            OpenApiExample(
                "Promote to District Leader",
                value={"role": "DISTRICT_LEADER", "district": 3, "is_active": True},
                request_only=True,
            )
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["👥 Users"],
        summary="Deactivate user account",
        description=(
            "Soft-deactivates a user account by setting `is_active=false`. "
            "The user record is NOT deleted from the database. **Admin only.**"
        ),
        responses={204: OpenApiResponse(description="User deactivated")},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    @extend_schema(
        tags=["👥 Users"],
        summary="User activity log",
        description=(
            "Returns the last 50 audit log entries for this user — all their CREATE, UPDATE, DELETE, and LOGIN actions."
        ),
        responses={
            200: OpenApiResponse(
                description="Audit log entries",
                examples=[
                    OpenApiExample(
                        "Activity log",
                        value={
                            "success": True,
                            "data": [
                                {
                                    "id": 1,
                                    "action": "CREATE",
                                    "resource_type": "Cow",
                                    "resource_id": 42,
                                    "old_values": None,
                                    "new_values": {"tag_number": "RW-GAS-001", "breed": "FRIESIAN_CROSS"},
                                    "ip_address": "197.243.12.45",
                                    "created_at": "2026-05-02T09:15:00+02:00",
                                }
                            ],
                        },
                    )
                ],
            )
        },
    )
    @action(detail=True, methods=["get"])
    def activity(self, request, pk=None):
        user = self.get_object()
        logs = AuditLog.objects.filter(user=user).order_by("-created_at")[:50]
        return Response(AuditLogSerializer(logs, many=True).data)
