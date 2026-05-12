
from rest_framework import serializers
from .models import WeatherData

class WeatherDataSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.district_name", read_only=True)
    class Meta:
        model = WeatherData
        fields = "__all__"
