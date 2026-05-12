from django.db import models


class MilkProduction(models.Model):
    cow             = models.ForeignKey("cows.Cow", on_delete=models.CASCADE, related_name="milk_records")
    morning_yield   = models.FloatField(null=True, blank=True)
    evening_yield   = models.FloatField(null=True, blank=True)
    daily_yield     = models.FloatField()
    feed_amount     = models.FloatField(null=True, blank=True)
    water_intake    = models.FloatField(null=True, blank=True)
    lstm_forecast   = models.FloatField(null=True, blank=True)
    model           = models.ForeignKey("predictions.AIModel", on_delete=models.SET_NULL, null=True, blank=True)
    collection_date = models.DateField()
    notes           = models.TextField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "milk_production"
        ordering = ["-collection_date"]
        unique_together = [("cow", "collection_date")]
        indexes = [models.Index(fields=["cow", "collection_date"])]

    def __str__(self): return f"Milk {self.cow.tag_number} on {self.collection_date}: {self.daily_yield}L"
