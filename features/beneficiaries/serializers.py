
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Beneficiary
from shared.exceptions import InvalidUbudehe


class BeneficiarySerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.district_name", read_only=True)
    active_cows   = serializers.SerializerMethodField()

    class Meta:
        model = Beneficiary
        fields = ["id","national_id","full_name","ubudehe_category","phone_number","district",
                  "district_name","gender","ml_risk_profile","registration_date","is_active",
                  "deregistered_at","deregister_reason","active_cows","created_at"]
        read_only_fields = ["id","ml_risk_profile","created_at"]

    @extend_schema_field(serializers.IntegerField)
    def get_active_cows(self, obj) -> int:
        return obj.cows.filter(is_alive=True).count()

    def validate_ubudehe_category(self, value):
        if value not in (1, 2):
            raise serializers.ValidationError("Only Ubudehe category 1 or 2 qualifies for Girinka.")
        return value


class BeneficiaryCreateSerializer(BeneficiarySerializer):
    pass


class DeregisterSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(choices=[
        "NO_LONGER_ELIGIBLE","COW_DIED","RULE_VIOLATION","RELOCATED","VOLUNTARY","DECEASED","LAND_LOSS"
    ])
    notes  = serializers.CharField(required=False, allow_blank=True)
