
from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    cow_tag          = serializers.CharField(source="cow.tag_number", read_only=True)
    beneficiary_name = serializers.CharField(source="beneficiary.full_name", read_only=True)
    class Meta:
        model = Alert
        fields = "__all__"
        read_only_fields = ["id","alert_timestamp"]
