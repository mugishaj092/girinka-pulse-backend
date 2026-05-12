from django.db import models


class WeatherData(models.Model):
    district     = models.ForeignKey("districts.District", on_delete=models.CASCADE, related_name="weather_records")
    temperature  = models.FloatField(null=True, blank=True)
    humidity     = models.FloatField(null=True, blank=True)
    rainfall     = models.FloatField(null=True, blank=True)
    wind_speed   = models.FloatField(null=True, blank=True)
    reading_time = models.DateTimeField()
    data_source  = models.CharField(max_length=30, default="OpenMeteo")
    forecast_day = models.IntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "weather_data"
        ordering = ["-reading_time"]
        indexes = [models.Index(fields=["district", "reading_time"])]

    def __str__(self): return f"Weather {self.district} {self.reading_time}"
