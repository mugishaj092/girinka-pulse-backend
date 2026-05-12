from django.db import models


class MLRiskProfile(models.TextChoices):
    LOW      = "LOW",      "Low"
    MEDIUM   = "MEDIUM",   "Medium"
    HIGH     = "HIGH",     "High"
    CRITICAL = "CRITICAL", "Critical"


class DeregisterReason(models.TextChoices):
    NO_LONGER_ELIGIBLE = "NO_LONGER_ELIGIBLE", "No Longer Eligible"
    COW_DIED           = "COW_DIED",           "Cow Died"
    RULE_VIOLATION     = "RULE_VIOLATION",      "Rule Violation"
    RELOCATED          = "RELOCATED",           "Relocated"
    VOLUNTARY          = "VOLUNTARY",           "Voluntary"
    DECEASED           = "DECEASED",            "Beneficiary Deceased"
    LAND_LOSS          = "LAND_LOSS",           "Loss of Land"


class Beneficiary(models.Model):
    user              = models.OneToOneField("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="beneficiary_profile")
    district          = models.ForeignKey("districts.District", on_delete=models.PROTECT, related_name="beneficiaries")
    national_id       = models.CharField(max_length=16, unique=True)
    full_name         = models.CharField(max_length=100)
    ubudehe_category  = models.IntegerField()
    phone_number      = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth     = models.DateField(null=True, blank=True)
    gender            = models.CharField(max_length=10, choices=[("MALE","Male"),("FEMALE","Female")], null=True, blank=True)
    ml_risk_profile   = models.CharField(max_length=10, choices=MLRiskProfile.choices, default=MLRiskProfile.LOW)
    registration_date = models.DateField()
    is_active         = models.BooleanField(default=True)
    deregistered_at   = models.DateTimeField(null=True, blank=True)
    deregister_reason = models.CharField(max_length=30, choices=DeregisterReason.choices, null=True, blank=True)
    deregister_notes  = models.TextField(null=True, blank=True)
    deregistered_by   = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="deregistrations")
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "beneficiaries"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["national_id"]),
            models.Index(fields=["district"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self): return f"{self.full_name} ({self.national_id})"

    def validate_ubudehe(self):
        if self.ubudehe_category not in (1, 2):
            from shared.exceptions import InvalidUbudehe
            raise InvalidUbudehe()
