from django.db import models


class ModelType(models.TextChoices):
    CATBOOST            = "CATBOOST",            "CatBoost"
    LSTM                = "LSTM",                "LSTM"
    RANDOM_FOREST       = "RANDOM_FOREST",       "Random Forest"
    LOGISTIC_REGRESSION = "LOGISTIC_REGRESSION", "Logistic Regression"


class PredictionType(models.TextChoices):
    MORTALITY_RISK     = "MORTALITY_RISK",     "Mortality Risk"
    MILK_FORECAST      = "MILK_FORECAST",      "Milk Forecast"
    DISEASE_RISK       = "DISEASE_RISK",       "Disease Risk"
    BIRTH_PROBABILITY  = "BIRTH_PROBABILITY",  "Birth Probability"
    PASS_ON_ELIGIBILITY= "PASS_ON_ELIGIBILITY","Pass-On Eligibility"


class AIModel(models.Model):
    model_type            = models.CharField(max_length=25, choices=ModelType.choices)
    version               = models.CharField(max_length=10)
    accuracy_metric       = models.FloatField(null=True, blank=True)
    r2_score              = models.FloatField(null=True, blank=True)
    mae                   = models.FloatField(null=True, blank=True)
    rmse                  = models.FloatField(null=True, blank=True)
    last_training_date    = models.DateTimeField(null=True, blank=True)
    training_data_source  = models.CharField(max_length=200, null=True, blank=True)
    training_samples      = models.IntegerField(null=True, blank=True)
    feature_columns       = models.JSONField(null=True, blank=True)
    is_deployed           = models.BooleanField(default=False)
    model_file_path       = models.CharField(max_length=500, null=True, blank=True)
    scaler_file_path      = models.CharField(max_length=500, null=True, blank=True)
    created_at            = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_models"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["model_type", "is_deployed"])]

    def __str__(self): return f"{self.model_type} {self.version}"


class PredictionLog(models.Model):
    cow             = models.ForeignKey("cows.Cow", on_delete=models.CASCADE, related_name="predictions")
    model           = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    prediction_type = models.CharField(max_length=25, choices=PredictionType.choices)
    input_features  = models.JSONField()
    output_values   = models.JSONField()
    confidence_score= models.FloatField(null=True, blank=True)
    predicted_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "prediction_logs"
        ordering = ["-predicted_at"]
        indexes = [models.Index(fields=["cow", "prediction_type"]), models.Index(fields=["predicted_at"])]

    def __str__(self): return f"{self.prediction_type} for {self.cow.tag_number}"
