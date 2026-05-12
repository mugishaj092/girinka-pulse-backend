from django.db import models


class Report(models.Model):
    generated_by  = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="reports")
    district      = models.ForeignKey("districts.District", on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")
    report_type   = models.CharField(max_length=30, choices=[
        ("FARMER_SUMMARY","Farmer Summary"),("DISTRICT_WEEKLY","District Weekly"),
        ("NATIONAL_MONTHLY","National Monthly"),("VET_PRIORITY","Vet Priority"),
        ("PASS_ON_AUDIT","Pass-On Audit"),("AI_PERFORMANCE","AI Performance"),
    ])
    report_period = models.CharField(max_length=10, choices=[
        ("DAILY","Daily"),("WEEKLY","Weekly"),("MONTHLY","Monthly"),("ANNUAL","Annual"),
    ])
    period_start  = models.DateField(null=True, blank=True)
    period_end    = models.DateField(null=True, blank=True)
    data_snapshot = models.JSONField(null=True, blank=True)
    file_url      = models.URLField(null=True, blank=True)
    status        = models.CharField(max_length=12, choices=[
        ("PENDING","Pending"),("GENERATING","Generating"),("READY","Ready"),("FAILED","Failed"),
    ], default="PENDING")
    generated_at  = models.DateTimeField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reports"
        ordering = ["-created_at"]

    def __str__(self): return f"{self.report_type} ({self.status})"
