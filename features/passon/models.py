from django.db import models


class PassOnStatus(models.TextChoices):
    PENDING   = "PENDING",   "Pending"
    APPROVED  = "APPROVED",  "Approved"
    COMPLETED = "COMPLETED", "Completed"
    REJECTED  = "REJECTED",  "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"


class PassOnRegistry(models.Model):
    calf                   = models.ForeignKey("cows.Cow", on_delete=models.PROTECT, related_name="passon_records")
    donor_farmer           = models.ForeignKey("beneficiaries.Beneficiary", on_delete=models.PROTECT, related_name="passon_donations")
    recipient_farmer       = models.ForeignKey("beneficiaries.Beneficiary", on_delete=models.PROTECT, related_name="passon_receipts")
    district               = models.ForeignKey("districts.District", on_delete=models.PROTECT)
    eligibility_score      = models.FloatField(null=True, blank=True)
    transfer_date          = models.DateField()
    cell_leader_approval   = models.BooleanField(default=False)
    approved_by            = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="passon_approvals")
    approval_date          = models.DateTimeField(null=True, blank=True)
    status                 = models.CharField(max_length=12, choices=PassOnStatus.choices, default=PassOnStatus.PENDING)
    notes                  = models.TextField(null=True, blank=True)
    certificate_url        = models.URLField(null=True, blank=True)
    created_at             = models.DateTimeField(auto_now_add=True)
    updated_at             = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "passon_registry"
        ordering = ["-created_at"]

    def __str__(self): return f"PassOn #{self.id}: {self.calf.tag_number} → {self.recipient_farmer}"
