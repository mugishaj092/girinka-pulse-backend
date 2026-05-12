from django.db import models


class AlertType(models.TextChoices):
    MORTALITY_RISK   = "MORTALITY_RISK",   "Mortality Risk"
    LOW_MILK         = "LOW_MILK",         "Low Milk Production"
    DISEASE_OUTBREAK = "DISEASE_OUTBREAK", "Disease Outbreak"
    WEATHER_RISK     = "WEATHER_RISK",     "Weather Risk"
    VET_VISIT_DUE    = "VET_VISIT_DUE",   "Vet Visit Due"
    PASS_ON_DUE      = "PASS_ON_DUE",     "Pass-On Due"


class AlertSeverity(models.TextChoices):
    INFO     = "INFO",     "Info"
    WARNING  = "WARNING",  "Warning"
    URGENT   = "URGENT",   "Urgent"
    CRITICAL = "CRITICAL", "Critical"


class Alert(models.Model):
    cow              = models.ForeignKey("cows.Cow", on_delete=models.CASCADE, related_name="alerts")
    model            = models.ForeignKey("predictions.AIModel", on_delete=models.SET_NULL, null=True, blank=True)
    beneficiary      = models.ForeignKey("beneficiaries.Beneficiary", on_delete=models.CASCADE, related_name="alerts")
    alert_type       = models.CharField(max_length=20, choices=AlertType.choices)
    severity         = models.CharField(max_length=10, choices=AlertSeverity.choices)
    risk_score       = models.FloatField(null=True, blank=True)
    message          = models.TextField(null=True, blank=True)
    recommendation   = models.TextField(null=True, blank=True)
    sent_via_sms     = models.BooleanField(default=False)
    sms_sent_at      = models.DateTimeField(null=True, blank=True)
    is_resolved      = models.BooleanField(default=False)
    resolved_at      = models.DateTimeField(null=True, blank=True)
    resolved_by      = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_alerts")
    resolution_notes = models.TextField(null=True, blank=True)
    alert_timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alerts"
        ordering = ["-alert_timestamp"]
        indexes = [
            models.Index(fields=["cow"]),
            models.Index(fields=["is_resolved"]),
            models.Index(fields=["severity"]),
        ]

    def __str__(self): return f"[{self.severity}] {self.alert_type} - Cow {self.cow.tag_number}"


class NotificationLog(models.Model):
    alert       = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="notifications")
    recipient   = models.ForeignKey("users.User", on_delete=models.CASCADE)
    channel     = models.CharField(max_length=10, choices=[("SMS","SMS"),("EMAIL","Email"),("IN_APP","In App"),("PUSH","Push")])
    status      = models.CharField(max_length=10, choices=[("SENT","Sent"),("DELIVERED","Delivered"),("FAILED","Failed"),("PENDING","Pending")])
    sent_at     = models.DateTimeField(null=True, blank=True)
    delivered_at= models.DateTimeField(null=True, blank=True)
    error_message=models.TextField(null=True, blank=True)

    class Meta:
        db_table = "notification_logs"
