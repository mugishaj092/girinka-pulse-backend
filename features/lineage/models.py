from django.db import models


class LineageRecord(models.Model):
    cow              = models.OneToOneField("cows.Cow", on_delete=models.CASCADE, related_name="lineage")
    mother           = models.ForeignKey("cows.Cow", on_delete=models.SET_NULL, null=True, blank=True, related_name="offspring")
    father_id        = models.BigIntegerField(null=True, blank=True)
    birth_date       = models.DateField(null=True, blank=True)
    birth_weight     = models.FloatField(null=True, blank=True)
    birth_health     = models.CharField(max_length=12, choices=[("EXCELLENT","Excellent"),("GOOD","Good"),("FAIR","Fair"),("POOR","Poor")], null=True, blank=True)
    genetic_notes    = models.TextField(null=True, blank=True)
    generation_number= models.IntegerField(default=1)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lineage_records"

    def __str__(self): return f"Lineage: {self.cow.tag_number}"
