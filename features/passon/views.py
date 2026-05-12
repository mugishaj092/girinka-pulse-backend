
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from shared.permissions import IsCellLeaderOrAbove
from .models import PassOnRegistry, PassOnStatus
from .serializers import PassOnSerializer


class PassOnViewSet(viewsets.ModelViewSet):
    queryset = PassOnRegistry.objects.select_related("calf", "donor_farmer", "recipient_farmer", "district").all()
    serializer_class = PassOnSerializer
    permission_classes = [IsCellLeaderOrAbove]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role in ("CELL_LEADER", "VETERINARIAN", "DISTRICT_LEADER"):
            return qs.filter(district=user.district)
        return qs

    @extend_schema(
        tags=["🔄 Pass-On"],
        summary="List pass-on transfers",
        description=(
            "Returns all calf pass-on transfers. "
            "Cell Leaders see their district only. Admins see all nationally.\n\n"
            "Filter by `status` (`PENDING`, `APPROVED`, `COMPLETED`, `REJECTED`, `CANCELLED`) "
            "or `district`."
        ),
        responses={200: PassOnSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🔄 Pass-On"],
        summary="Initiate a calf pass-on transfer",
        description=(
            "Create a new calf pass-on transfer record. Status starts as `PENDING`. "
            "The Cell Leader must approve before the transfer can be completed."
        ),
        request=PassOnSerializer,
        responses={
            201: PassOnSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "New transfer",
                value={
                    "calf": 58,
                    "donor_farmer": 12,
                    "recipient_farmer": 31,
                    "district": 7,
                    "transfer_date": "2026-05-15",
                    "notes": "Calf is healthy. Recipient household has been verified.",
                },
                request_only=True,
            )
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["🔄 Pass-On"],
        summary="Get transfer details",
        description=(
            "Full transfer details including donor, recipient, calf, eligibility score, "
            "approval status, and certificate URL."
        ),
        responses={200: PassOnSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🔄 Pass-On"],
        summary="Update transfer",
        description="Update transfer details such as notes or transfer date.",
        request=PassOnSerializer,
        responses={200: PassOnSerializer},
        examples=[
            OpenApiExample(
                "Reschedule transfer",
                value={"transfer_date": "2026-05-20", "notes": "Transfer date moved — recipient unavailable."},
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
        tags=["🔄 Pass-On"],
        summary="Approve transfer",
        description=(
            "Cell Leader approves the calf transfer. "
            "Sets `cell_leader_approval=true` and changes status to `APPROVED`."
        ),
        request=None,
        responses={
            200: OpenApiResponse(
                description="Transfer approved",
                examples=[
                    OpenApiExample(
                        "Approved",
                        value={
                            "success": True,
                            "data": {
                                "id": 14,
                                "status": "APPROVED",
                                "cell_leader_approval": True,
                                "approved_by": 1,
                                "approval_date": "2026-05-03T10:00:00+02:00",
                            },
                        },
                    )
                ],
            )
        },
    )
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        transfer = self.get_object()
        transfer.cell_leader_approval = True
        transfer.approved_by = request.user
        transfer.approval_date = timezone.now()
        transfer.status = PassOnStatus.APPROVED
        transfer.save(update_fields=["cell_leader_approval", "approved_by", "approval_date", "status"])
        
        # Create in-app notifications
        from features.notifications.models import Notification
        
        # Notify donor
        if transfer.donor_farmer.user:
            Notification.objects.create(
                user=transfer.donor_farmer.user,
                title="✅ Pass-On Transfer Approved",
                message=f"Your calf transfer ({transfer.calf.tag_number}) to {transfer.recipient_farmer.full_name} has been approved by the cell leader.",
            )
        
        # Notify recipient
        if transfer.recipient_farmer.user:
            Notification.objects.create(
                user=transfer.recipient_farmer.user,
                title="✅ Pass-On Transfer Approved",
                message=f"You have been approved to receive calf {transfer.calf.tag_number} from {transfer.donor_farmer.full_name}. Transfer date: {transfer.transfer_date}.",
            )
        
        return Response(PassOnSerializer(transfer).data)

    @extend_schema(
        tags=["🔄 Pass-On"],
        summary="Complete transfer",
        description=(
            "Mark the transfer as complete. Changes calf ownership in the database. "
            "Triggers certificate generation on Cloudinary and emails both parties via Resend."
        ),
        request=None,
        responses={
            200: OpenApiResponse(
                description="Transfer completed",
                examples=[
                    OpenApiExample(
                        "Completed",
                        value={"success": True, "data": {"id": 14, "status": "COMPLETED", "calf_tag": "RW-BUG-2025-058"}},
                    )
                ],
            )
        },
    )
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        transfer = self.get_object()
        transfer.status = PassOnStatus.COMPLETED
        transfer.save(update_fields=["status"])
        transfer.calf.beneficiary = transfer.recipient_farmer
        transfer.calf.save(update_fields=["beneficiary"])
        
        # Create in-app notifications
        from features.notifications.models import Notification
        
        # Notify donor
        if transfer.donor_farmer.user:
            Notification.objects.create(
                user=transfer.donor_farmer.user,
                title="🎉 Pass-On Transfer Completed",
                message=f"Your calf {transfer.calf.tag_number} has been successfully transferred to {transfer.recipient_farmer.full_name}. Certificate will be sent via email.",
            )
        
        # Notify recipient
        if transfer.recipient_farmer.user:
            Notification.objects.create(
                user=transfer.recipient_farmer.user,
                title="🎉 Welcome Your New Calf!",
                message=f"Congratulations! You are now the owner of calf {transfer.calf.tag_number}. Certificate will be sent via email.",
            )
        
        from features.passon.tasks import generate_passon_certificate
        generate_passon_certificate.delay(transfer.id)
        return Response(PassOnSerializer(transfer).data)

    @extend_schema(
        tags=["🔄 Pass-On"],
        summary="Reject transfer",
        description="Reject a transfer with a reason. Sets status to `REJECTED`.",
        request=None,
        responses={
            200: OpenApiResponse(
                description="Transfer rejected",
                examples=[
                    OpenApiExample(
                        "Rejected",
                        value={
                            "success": True,
                            "data": {
                                "id": 14,
                                "status": "REJECTED",
                                "notes": "Recipient household failed land verification check.",
                            },
                        },
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Rejection reason",
                value={"notes": "Recipient household failed land verification check."},
                request_only=True,
            )
        ],
    )
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        transfer = self.get_object()
        transfer.status = PassOnStatus.REJECTED
        transfer.notes = request.data.get("notes", "")
        transfer.save(update_fields=["status", "notes"])
        
        # Create in-app notifications
        from features.notifications.models import Notification
        
        # Notify donor
        if transfer.donor_farmer.user:
            Notification.objects.create(
                user=transfer.donor_farmer.user,
                title="❌ Pass-On Transfer Rejected",
                message=f"Your calf transfer ({transfer.calf.tag_number}) to {transfer.recipient_farmer.full_name} has been rejected. Reason: {transfer.notes}",
            )
        
        # Notify recipient
        if transfer.recipient_farmer.user:
            Notification.objects.create(
                user=transfer.recipient_farmer.user,
                title="❌ Pass-On Transfer Rejected",
                message=f"The calf transfer from {transfer.donor_farmer.full_name} has been rejected. Reason: {transfer.notes}",
            )
        
        return Response(PassOnSerializer(transfer).data)

    @extend_schema(
        tags=["🔄 Pass-On"],
        summary="Get transfer certificate URL",
        description=(
            "Returns the Cloudinary URL of the transfer certificate. "
            "Available only after the transfer status is `COMPLETED`."
        ),
        responses={
            200: OpenApiResponse(
                description="Certificate URL",
                examples=[
                    OpenApiExample(
                        "Certificate ready",
                        value={
                            "success": True,
                            "data": {
                                "certificate_url": "https://res.cloudinary.com/dhforyx1s/raw/upload/girinka/certificates/certificate_14.html"
                            },
                        },
                    )
                ],
            ),
            404: OpenApiResponse(description="Certificate not yet generated"),
        },
    )
    @action(detail=True, methods=["get"])
    def certificate(self, request, pk=None):
        transfer = self.get_object()
        if not transfer.certificate_url:
            return Response({"detail": "Certificate not yet generated."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"certificate_url": transfer.certificate_url})
