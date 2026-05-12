from django.db import models


class CowBreed(models.TextChoices):
    FRIESIAN       = "FRIESIAN",       "Friesian"
    JERSEY         = "JERSEY",         "Jersey"
    ANKOLE         = "ANKOLE",         "Ankole"
    ANKOLE_CROSS   = "ANKOLE_CROSS",   "Ankole Cross"
    FRIESIAN_CROSS = "FRIESIAN_CROSS", "Friesian Cross"
    JERSEY_CROSS   = "JERSEY_CROSS",   "Jersey Cross"
    OTHER          = "OTHER",          "Other"


class HealthStatus(models.TextChoices):
    HEALTHY            = "HEALTHY",            "Healthy"
    AT_RISK            = "AT_RISK",            "At Risk"
    HIGH_RISK          = "HIGH_RISK",          "High Risk"
    UNDER_TREATMENT    = "UNDER_TREATMENT",    "Under Treatment"
    CRITICAL           = "CRITICAL",           "Critical"
    EMERGENCY          = "EMERGENCY",          "Emergency"
    DECEASED           = "DECEASED",           "Deceased"
    FLAGGED_FOR_REVIEW = "FLAGGED_FOR_REVIEW", "Flagged for Review"


class OriginType(models.TextChoices):
    DIRECT_PROGRAM    = "DIRECT_PROGRAM",    "Direct Program"
    BORN_ON_FARM      = "BORN_ON_FARM",      "Born on Farm"
    PASS_ON_RECEIVED  = "PASS_ON_RECEIVED",  "Pass-On Received"


class Cow(models.Model):
    beneficiary           = models.ForeignKey("beneficiaries.Beneficiary", on_delete=models.PROTECT, related_name="cows")
    district              = models.ForeignKey("districts.District", on_delete=models.PROTECT, related_name="cows")
    tag_number            = models.CharField(max_length=20, unique=True)
    breed                 = models.CharField(max_length=20, choices=CowBreed.choices, default=CowBreed.FRIESIAN_CROSS)
    dob                   = models.DateField(null=True, blank=True)
    health_status         = models.CharField(max_length=20, choices=HealthStatus.choices, default=HealthStatus.HEALTHY)
    genetic_profile_id    = models.CharField(max_length=50, null=True, blank=True)
    mortality_risk_score  = models.FloatField(null=True, blank=True)
    origin_type           = models.CharField(max_length=20, choices=OriginType.choices, default=OriginType.DIRECT_PROGRAM)
    is_alive              = models.BooleanField(default=True)
    death_date            = models.DateField(null=True, blank=True)
    death_cause           = models.TextField(null=True, blank=True)
    death_confirmed_by    = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="confirmed_deaths")
    lactation_number      = models.IntegerField(default=1)
    days_in_milk          = models.IntegerField(default=0)
    created_at            = models.DateTimeField(auto_now_add=True)
    updated_at            = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cows"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tag_number"]),
            models.Index(fields=["beneficiary"]),
            models.Index(fields=["health_status"]),
            models.Index(fields=["is_alive"]),
        ]

    def __str__(self): return f"Cow #{self.tag_number} ({self.breed})"

    @property
    def age_months(self):
        if not self.dob:
            return None
        from datetime import date
        delta = date.today() - self.dob
        return int(delta.days / 30.44)

    def record_death(self, cause: str, confirmed_by):
        from datetime import date
        from shared.exceptions import CowAlreadyDeceasedError
        if not self.is_alive:
            raise CowAlreadyDeceasedError()
        self.is_alive = False
        self.death_date = date.today()
        self.death_cause = cause
        self.health_status = HealthStatus.DECEASED
        self.death_confirmed_by = confirmed_by
        self.save(update_fields=["is_alive", "death_date", "death_cause", "health_status", "death_confirmed_by"])
