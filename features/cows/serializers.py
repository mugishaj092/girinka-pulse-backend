
from rest_framework import serializers
from .models import Cow


class CowSerializer(serializers.ModelSerializer):
    beneficiary_name = serializers.CharField(source="beneficiary.full_name", read_only=True)
    district_name    = serializers.CharField(source="district.district_name", read_only=True)
    age_months       = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cow
        fields = ["id","tag_number","breed","dob","age_months","health_status","mortality_risk_score",
                  "origin_type","is_alive","death_date","lactation_number","days_in_milk",
                  "beneficiary","beneficiary_name","district","district_name","created_at"]
        read_only_fields = ["id","mortality_risk_score","created_at","age_months"]


class CowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cow
        fields = ["tag_number","breed","dob","beneficiary","district","origin_type"]


class CowDeathSerializer(serializers.Serializer):
    cause = serializers.CharField(max_length=500)
