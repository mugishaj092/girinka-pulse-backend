
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from shared.permissions import IsCellLeaderOrAbove, IsDistrictLeaderOrAdmin
from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsCellLeaderOrAbove]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role in ("CELL_LEADER", "VETERINARIAN"):
            return qs.filter(district=user.district)
        return qs

    @extend_schema(
        tags=["📊 Reports"],
        summary="List generated reports",
        description=(
            "Lists generated reports. Cell Leaders see their district only. Admins see all.\n\n"
            "Filter by `status` (`PENDING`, `GENERATING`, `READY`, `FAILED`) or `report_type`."
        ),
        responses={200: ReportSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["📊 Reports"],
        summary="Get report status",
        description="Returns the report status, data snapshot, and Cloudinary file URL once ready.",
        responses={
            200: OpenApiResponse(
                description="Report detail",
                examples=[
                    OpenApiExample(
                        "Ready report",
                        value={
                            "success": True,
                            "data": {
                                "id": 7,
                                "report_type": "DISTRICT_WEEKLY",
                                "status": "READY",
                                "data_snapshot": {
                                    "total_cows": 1240,
                                    "total_beneficiaries": 980,
                                    "at_risk_cows": 87,
                                    "critical_cows": 12,
                                    "deceased_cows": 3,
                                    "unresolved_alerts": 14,
                                },
                                "file_url": "https://res.cloudinary.com/dhforyx1s/raw/upload/girinka/reports/report_7.html",
                                "generated_at": "2026-05-02T08:15:00+02:00",
                            },
                        },
                    )
                ],
            )
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["📊 Reports"],
        summary="Generate a new report",
        description=(
            "Queue a new report for generation. Uploaded to Cloudinary and emailed to the requester when ready.\n\n"
            "**Report type options:** `FARMER_SUMMARY` · `DISTRICT_WEEKLY` · `NATIONAL_MONTHLY` · "
            "`VET_PRIORITY` · `PASS_ON_AUDIT` · `AI_PERFORMANCE`"
        ),
        request=ReportSerializer,
        responses={
            202: OpenApiResponse(
                description="Report generation queued",
                examples=[
                    OpenApiExample(
                        "Queued",
                        value={
                            "success": True,
                            "data": {
                                "id": 8,
                                "status": "PENDING",
                                "report_type": "DISTRICT_WEEKLY",
                                "created_at": "2026-05-02T14:00:00+02:00",
                            },
                        },
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Weekly district report",
                value={
                    "report_type": "DISTRICT_WEEKLY",
                    "report_period": "WEEKLY",
                    "district": 3,
                    "period_start": "2026-04-25",
                    "period_end": "2026-05-02",
                },
                request_only=True,
            )
        ],
    )
    @action(detail=False, methods=["post"])
    def generate(self, request):
        serializer = ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save(generated_by=request.user)
        from .tasks import generate_report_pdf
        generate_report_pdf.delay(report.id)
        return Response(ReportSerializer(report).data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        tags=["📊 Reports"],
        summary="Download report",
        description="Returns the Cloudinary signed URL to download the report file. Returns 404 if the report is not yet ready.",
        responses={
            200: OpenApiResponse(
                description="Download URL",
                examples=[
                    OpenApiExample(
                        "Ready",
                        value={
                            "success": True,
                            "data": {
                                "download_url": "https://res.cloudinary.com/dhforyx1s/raw/upload/girinka/reports/report_7.html"
                            },
                        },
                    )
                ],
            ),
            404: OpenApiResponse(description="Report not ready"),
        },
    )
    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        report = self.get_object()
        if not report.file_url:
            return Response({"detail": "Report not ready."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"download_url": report.file_url})

    @extend_schema(
        tags=["📊 Reports"],
        summary="National live statistics",
        description=(
            "Returns live national statistics without generating a report file. "
            "**District Leader and Admin only.**"
        ),
        responses={
            200: OpenApiResponse(
                description="National statistics",
                examples=[
                    OpenApiExample(
                        "National stats",
                        value={
                            "success": True,
                            "data": {
                                "total_cows": 398420,
                                "total_beneficiaries": 496380,
                                "at_risk_cows": 24310,
                                "critical_cows": 3820,
                                "deceased_cows": 1240,
                                "unresolved_alerts": 8920,
                            },
                        },
                    )
                ],
            )
        },
    )
    @action(detail=False, methods=["get"], permission_classes=[IsDistrictLeaderOrAdmin])
    def national(self, request):
        from features.cows.models import Cow
        from features.beneficiaries.models import Beneficiary
        from features.alerts.models import Alert
        return Response({
            "total_cows": Cow.objects.filter(is_alive=True).count(),
            "at_risk_cows": Cow.objects.filter(
                health_status__in=["AT_RISK", "HIGH_RISK", "CRITICAL", "EMERGENCY"], is_alive=True
            ).count(),
            "critical_cows": Cow.objects.filter(
                health_status__in=["CRITICAL", "EMERGENCY"], is_alive=True
            ).count(),
            "deceased_cows": Cow.objects.filter(is_alive=False).count(),
            "total_beneficiaries": Beneficiary.objects.filter(is_active=True).count(),
            "unresolved_alerts": Alert.objects.filter(is_resolved=False).count(),
        })
