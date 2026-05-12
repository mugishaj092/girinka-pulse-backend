"""Auth views — JWT login/logout, OTP via Resend email."""
# Auto-reload test -
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import serializers as s

from features.users.models import User, OTPCode
from features.users.serializers import UserSerializer
from shared.utils import generate_otp
from .serializers import (
    LoginSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, PasswordChangeSerializer,
)
import logging

logger = logging.getLogger(__name__)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["🔑 Auth"],
        summary="Login — get JWT tokens",
        description=(
            "Authenticate with username and password. Returns an **access token** (1 hour) "
            "and a **refresh token** (7 days). Include the access token in every subsequent "
            "request as `Authorization: Bearer <access_token>`."
        ),
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Login successful",
                examples=[OpenApiExample(
                    "Success",
                    value={
                        "success": True,
                        "data": {
                            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "user": {
                                "id": 1, "username": "mugisha_joseph",
                                "full_name": "MUGISHA Joseph",
                                "role": "CELL_LEADER",
                                "district": 3,
                            },
                        },
                        "message": "OK", "errors": None, "meta": None,
                    },
                )],
            ),
            400: OpenApiResponse(description="Invalid credentials"),
        },
        examples=[
            OpenApiExample(
                "Farmer login",
                value={"username": "farmer_jean", "password": "securepass123"},
                request_only=True,
            ),
            OpenApiExample(
                "Admin login",
                value={"username": "admin", "password": "adminpass123"},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return Response({
            "access":  str(refresh.access_token),
            "refresh": str(refresh),
            "user":    UserSerializer(user).data,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["🔑 Auth"],
        summary="Logout — blacklist refresh token",
        description="Blacklists the refresh token so it can no longer be used. The access token will expire naturally after 1 hour.",
        request=inline_serializer("LogoutRequest", fields={"refresh": s.CharField()}),
        responses={200: OpenApiResponse(description="Logged out successfully")},
        examples=[OpenApiExample("Logout", value={"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}, request_only=True)],
    )
    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
            return Response({"detail": "Logged out successfully."})
        except TokenError:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["🔑 Auth"],
        summary="Refresh access token",
        description="Exchange a valid refresh token for a new access token. The refresh token is rotated on each use.",
        request=inline_serializer("RefreshRequest", fields={"refresh": s.CharField()}),
        responses={200: OpenApiResponse(description="New token pair returned")},
        examples=[OpenApiExample("Refresh", value={"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}, request_only=True)],
    )
    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            return Response({"access": str(token.access_token), "refresh": str(token)})
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["🔑 Auth"],
        summary="Request password reset OTP",
        description=(
            "Sends a 6-digit OTP to the registered email address via **Resend**. "
            "OTP expires in **10 minutes**. Does not reveal whether the email exists."
        ),
        request=PasswordResetRequestSerializer,
        responses={200: OpenApiResponse(description="OTP sent (if email is registered)")},
        examples=[OpenApiExample("Reset request", value={"email": "jean.baptiste@example.com"}, request_only=True)],
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
            otp = generate_otp()
            OTPCode.objects.create(user=user, code=otp, expires_at=timezone.now() + timedelta(minutes=10))
            from features.notifications.utils import send_password_reset_email
            send_password_reset_email(to=email, user_name=user.full_name, otp_code=otp)
        except User.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Password reset error: {e}", exc_info=True)
        return Response({"detail": "If this email is registered, a reset code has been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["🔑 Auth"],
        summary="Confirm password reset with OTP",
        description="Submit the 6-digit OTP from the email along with the new password.",
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(description="Password reset successful"),
            400: OpenApiResponse(description="Invalid or expired OTP"),
        },
        examples=[OpenApiExample(
            "Confirm reset",
            value={"email": "jean.baptiste@example.com", "otp_code": "482951", "new_password": "NewSecurePass@2026"},
            request_only=True,
        )],
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
            otp_obj = OTPCode.objects.filter(
                user=user, code=serializer.validated_data["otp_code"],
                is_used=False, expires_at__gt=timezone.now(),
            ).last()
            if not otp_obj:
                return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data["new_password"])
            user.save(update_fields=["password"])
            otp_obj.is_used = True
            otp_obj.save(update_fields=["is_used"])
            return Response({"detail": "Password reset successful."})
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["🔑 Auth"],
        summary="Change own password",
        description="Change the password for the currently authenticated user. Requires the current password for verification.",
        request=PasswordChangeSerializer,
        responses={200: OpenApiResponse(description="Password changed")},
        examples=[OpenApiExample(
            "Change password",
            value={"old_password": "OldPass@123", "new_password": "NewSecurePass@2026"},
            request_only=True,
        )],
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password changed successfully."})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["🔑 Auth"],
        summary="Get my profile",
        description="Returns the full profile of the currently authenticated user including role, district, and verification status.",
        responses={200: UserSerializer},
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @extend_schema(
        tags=["🔑 Auth"],
        summary="Update my profile",
        description="Update own profile fields. Farmers can update their email, phone, and name. Role and district cannot be self-modified.",
        request=inline_serializer("MeUpdateRequest", fields={
            "full_name":    s.CharField(required=False),
            "email":        s.EmailField(required=False),
            "phone_number": s.CharField(required=False),
        }),
        responses={200: UserSerializer},
        examples=[OpenApiExample(
            "Update name and phone",
            value={"full_name": "Jean Baptiste Nzeyimana", "phone_number": "+250788123456"},
            request_only=True,
        )],
    )
    def patch(self, request):
        from features.users.serializers import UserUpdateSerializer
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)
