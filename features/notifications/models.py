from django.db import models


class NotificationPreference(models.Model):
    user       = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="notification_prefs")
    sms        = models.BooleanField(default=True)
    email      = models.BooleanField(default=True)
    in_app     = models.BooleanField(default=True)
    push       = models.BooleanField(default=False)
    min_severity = models.CharField(max_length=10, default="INFO")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_preferences"


class Notification(models.Model):
    user       = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="notifications")
    alert      = models.ForeignKey("alerts.Alert", on_delete=models.CASCADE, null=True, blank=True)
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    read_at    = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_read"])]

    def __str__(self): return f"Notification for {self.user_id}: {self.title}"
