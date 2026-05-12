
from rest_framework import serializers
from .models import LineageRecord

class LineageSerializer(serializers.ModelSerializer):
    mother_tag = serializers.CharField(source="mother.tag_number", read_only=True)
    class Meta:
        model = LineageRecord
        fields = "__all__"
