from rest_framework import serializers
from .models import District


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class DistrictStatsSerializer(serializers.Serializer):
    total_cows         = serializers.IntegerField()
    at_risk_cows       = serializers.IntegerField()
    avg_milk           = serializers.FloatField()
    total_beneficiaries= serializers.IntegerField()
