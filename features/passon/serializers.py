
from rest_framework import serializers
from .models import PassOnRegistry


class PassOnSerializer(serializers.ModelSerializer):
    calf_tag            = serializers.CharField(source="calf.tag_number", read_only=True)
    donor_name          = serializers.CharField(source="donor_farmer.full_name", read_only=True)
    recipient_name      = serializers.CharField(source="recipient_farmer.full_name", read_only=True)
    class Meta:
        model = PassOnRegistry
        fields = "__all__"
        read_only_fields = ["id","eligibility_score","cell_leader_approval","approval_date","certificate_url","created_at"]
