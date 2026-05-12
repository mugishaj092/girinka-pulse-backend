
from rest_framework import serializers
from features.users.models import User
from .models import Veterinarian, HealthRecord


class VeterinarianSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    class Meta:
        model = Veterinarian
        fields = ["id","user","full_name","district","license_number","specialization","is_active","created_at"]


class HealthRecordSerializer(serializers.ModelSerializer):
    cow_tag  = serializers.CharField(source="cow.tag_number", read_only=True)
    vet_name = serializers.CharField(source="vet.user.full_name", read_only=True)
    vet      = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model  = HealthRecord
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def _resolve_vet(self, user_id):
        if user_id is None:
            return None
        try:
            user = User.objects.get(pk=user_id, role="VETERINARIAN", is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError({"vet": "No active VETERINARIAN user with this id."})
        try:
            return user.vet_profile
        except Veterinarian.DoesNotExist:
            raise serializers.ValidationError({"vet": "This vet user has no Veterinarian profile."})

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["vet"] = instance.vet.user_id if instance.vet else None
        return rep

    def create(self, validated_data):
        user_id = validated_data.pop("vet", None)
        validated_data["vet"] = self._resolve_vet(user_id)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "vet" in validated_data:
            validated_data["vet"] = self._resolve_vet(validated_data["vet"])
        return super().update(instance, validated_data)
