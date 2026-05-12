from django.db import models


class District(models.Model):
    district_name = models.CharField(max_length=100)
    province      = models.CharField(max_length=50)
    sector        = models.CharField(max_length=50, null=True, blank=True)
    cell          = models.CharField(max_length=50, null=True, blank=True)
    latitude      = models.FloatField(null=True, blank=True)
    longitude     = models.FloatField(null=True, blank=True)
    is_remote     = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "districts"
        ordering = ["district_name"]

    def __str__(self): return self.district_name

    def get_latest_weather(self):
        return self.weather_records.order_by("-reading_time").first()

    def get_stats(self):
        from django.db.models import Avg, Count
        cows = self.cows.filter(is_alive=True)
        return {
            "total_cows": cows.count(),
            "at_risk_cows": cows.filter(health_status__in=["AT_RISK","HIGH_RISK","CRITICAL","EMERGENCY"]).count(),
            "avg_milk": cows.aggregate(avg=Avg("milk_records__daily_yield"))["avg"] or 0,
            "total_beneficiaries": self.beneficiaries.filter(is_active=True).count(),
        }
