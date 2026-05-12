from django.db import models


class Veterinarian(models.Model):
    user           = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="vet_profile")
    district       = models.ForeignKey("districts.District", on_delete=models.PROTECT, related_name="vets")
    license_number = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=80, null=True, blank=True)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "veterinarians"

    def __str__(self): return f"Vet: {self.user.full_name}"


class HealthRecord(models.Model):
    cow                  = models.ForeignKey("cows.Cow", on_delete=models.CASCADE, related_name="health_records")
    vet                  = models.ForeignKey(Veterinarian, on_delete=models.SET_NULL, null=True, blank=True, related_name="health_records")
    diagnosis            = models.TextField(null=True, blank=True)
    treatment_given      = models.TextField(null=True, blank=True)
    symptoms             = models.TextField(null=True, blank=True)
    temperature          = models.FloatField(null=True, blank=True)
    weight               = models.FloatField(null=True, blank=True)
    mortality_risk_score = models.FloatField(null=True, blank=True)
    model                = models.ForeignKey("predictions.AIModel", on_delete=models.SET_NULL, null=True, blank=True)
    next_visit_date      = models.DateField(null=True, blank=True)
    date_recorded        = models.DateTimeField()
    created_at           = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_records"
        ordering = ["-date_recorded"]
        indexes = [models.Index(fields=["cow"]), models.Index(fields=["date_recorded"])]

    def __str__(self): return f"Health record for {self.cow.tag_number} on {self.date_recorded}"
