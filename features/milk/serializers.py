
from rest_framework import serializers
from .models import MilkProduction


class MilkProductionSerializer(serializers.ModelSerializer):
    cow_tag = serializers.CharField(source="cow.tag_number", read_only=True)
    class Meta:
        model = MilkProduction
        fields = "__all__"
        read_only_fields = ["id","lstm_forecast","created_at"]

    def validate(self, data):
        m = data.get("morning_yield", 0) or 0
        e = data.get("evening_yield", 0) or 0
        d = data.get("daily_yield", 0)
        if m and e and abs(d - (m+e)) > 0.5:
            raise serializers.ValidationError("daily_yield must equal morning_yield + evening_yield.")
        
        # Check for duplicate entry
        cow = data.get("cow")
        collection_date = data.get("collection_date")
        if cow and collection_date:
            if self.instance:  # Update case
                exists = MilkProduction.objects.filter(
                    cow=cow, collection_date=collection_date
                ).exclude(id=self.instance.id).exists()
            else:  # Create case
                exists = MilkProduction.objects.filter(
                    cow=cow, collection_date=collection_date
                ).exists()
            
            if exists:
                raise serializers.ValidationError({
                    "collection_date": f"A milk record for this cow on {collection_date} already exists. Please update the existing record instead."
                })
        
        return data
