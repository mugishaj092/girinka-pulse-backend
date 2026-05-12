
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import LineageRecord
from .serializers import LineageSerializer


class LineageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LineageRecord.objects.select_related("cow", "mother").all()
    serializer_class = LineageSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["🧬 Lineage"],
        summary="List lineage records",
        description=(
            "Returns cow lineage records. Filter by `cow_id` to retrieve the lineage "
            "for a specific cow."
        ),
        parameters=[
            OpenApiParameter("cow_id", OpenApiTypes.INT, description="Filter by cow ID"),
        ],
        responses={200: LineageSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        cow_id = request.query_params.get("cow_id")
        if cow_id:
            self.queryset = self.queryset.filter(cow_id=cow_id)
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["🧬 Lineage"],
        summary="Get lineage record",
        description="Returns a specific lineage record by ID.",
        responses={
            200: OpenApiResponse(
                description="Lineage record",
                examples=[
                    OpenApiExample(
                        "Cow lineage",
                        value={
                            "success": True,
                            "data": {
                                "id": 18,
                                "cow": 42,
                                "mother": 15,
                                "mother_tag": "RW-GAS-2020-015",
                                "father_id": None,
                                "birth_date": "2022-03-15",
                                "birth_weight": 32.5,
                                "birth_health": "GOOD",
                                "generation_number": 2,
                                "genetic_notes": "Strong milk genes from Friesian line",
                            },
                        },
                    )
                ],
            ),
            404: OpenApiResponse(description="Lineage record not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True)
    @action(detail=False, methods=["get"])
    def by_cow(self, request):
        cow_id = request.query_params.get("cow_id")
        try:
            record = LineageRecord.objects.get(cow_id=cow_id)
            return Response(LineageSerializer(record).data)
        except LineageRecord.DoesNotExist:
            return Response({"detail": "No lineage found."}, status=404)
