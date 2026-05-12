from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import serializers as s

from shared.permissions import IsCellLeaderOrAbove, IsVetOrAbove, IsAdmin
from features.cows.models import Cow
from .models import AIModel, PredictionLog
from .serializers import AIModelSerializer, PredictionLogSerializer
from .services import PredictionService
from .ml_client import ml_client


class MortalityPredictionView(APIView):
    permission_classes = [IsCellLeaderOrAbove]

    @extend_schema(
        tags=["🤖 Predictions"],
        summary="Run mortality risk prediction (CatBoost)",
        description=(
            "Runs the **CatBoost** mortality risk model for a specific cow. "
            "Returns a risk score from 0.0 (safe) to 1.0 (emergency).\n\n"
            "**Side effects:**\n"
            "- Updates `cow.mortality_risk_score` and `cow.health_status`\n"
            "- Creates an alert if score ≥ 0.50\n"
            "- Sends alert email if score ≥ 0.60\n\n"
            "**Risk levels:**\n"
            "| Score | Level | Action |\n"
            "|-------|-------|--------|\n"
            "| 0.90–1.00 | EMERGENCY | Immediate vet + email |\n"
            "| 0.80–0.89 | VERY_HIGH | Critical alert + email |\n"
            "| 0.60–0.79 | HIGH | Urgent vet |\n"
            "| 0.50–0.59 | MEDIUM | Schedule vet |\n"
            "| 0.00–0.49 | LOW | Monitor |\n"
        ),
        request=inline_serializer("MortalityRequest", fields={"cow_id": s.IntegerField()}),
        responses={
            200: OpenApiResponse(
                description="Prediction result",
                examples=[
                    OpenApiExample(
                        "High risk cow",
                        value={
                            "cow_id": 42, "mortality_risk_score": 0.7155,
                            "risk_level": "HIGH", "alert_triggered": True,
                            "alert_severity": "URGENT",
                            "recommended_action": "🔶 Urgent vet consultation within 24 hours. Monitor closely.",
                            "model_version": "v1.0.0",
                        },
                    ),
                    OpenApiExample(
                        "Healthy cow",
                        value={
                            "cow_id": 7, "mortality_risk_score": 0.09,
                            "risk_level": "LOW", "alert_triggered": False,
                            "alert_severity": "NONE",
                            "recommended_action": "✅ Cow appears healthy. Continue routine monthly monitoring.",
                            "model_version": "v1.0.0",
                        },
                    ),
                ],
            ),
            404: OpenApiResponse(description="Cow not found"),
        },
        examples=[
            OpenApiExample("Run for cow #42", value={"cow_id": 42}, request_only=True),
        ],
    )
    def post(self, request):
        cow_id = request.data.get("cow_id")
        try:
            cow = Cow.objects.get(id=cow_id)
        except Cow.DoesNotExist:
            return Response({"detail": "Cow not found."}, status=status.HTTP_404_NOT_FOUND)
        result = PredictionService.run_mortality_check(cow)
        return Response(result)


class MilkPredictionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["🤖 Predictions"],
        summary="Run 7-day milk forecast (LSTM)",
        description=(
            "Runs the **Bidirectional LSTM** milk forecast for a specific cow. "
            "Requires at least **7 days** of milk production records in the database.\n\n"
            "Returns daily predictions for the next 7 days plus total and average."
        ),
        request=inline_serializer("MilkForecastRequest", fields={"cow_id": s.IntegerField()}),
        responses={
            200: OpenApiResponse(
                description="7-day forecast",
                examples=[OpenApiExample(
                    "Healthy Friesian forecast",
                    value={
                        "cow_id": 7, "forecast_days": 7,
                        "forecasts": [
                            {"day": 1, "predicted_yield_litres": 12.3, "confidence": "high"},
                            {"day": 2, "predicted_yield_litres": 12.1, "confidence": "high"},
                            {"day": 3, "predicted_yield_litres": 11.9, "confidence": "high"},
                            {"day": 4, "predicted_yield_litres": 11.8, "confidence": "high"},
                            {"day": 5, "predicted_yield_litres": 11.7, "confidence": "high"},
                            {"day": 6, "predicted_yield_litres": 11.6, "confidence": "high"},
                            {"day": 7, "predicted_yield_litres": 11.4, "confidence": "high"},
                        ],
                        "avg_predicted_yield_litres": 11.97,
                        "total_predicted_litres": 83.8,
                        "data_quality": "sufficient",
                        "note": "Forecast based on ≥15 days of data — high confidence.",
                        "model_version": "v1.0.0",
                    },
                )],
            ),
            422: OpenApiResponse(description="INSUFFICIENT_MILK_DATA — need 7+ days"),
        },
        examples=[OpenApiExample("Forecast for cow #7", value={"cow_id": 7}, request_only=True)],
    )
    def post(self, request):
        cow_id = request.data.get("cow_id")
        try:
            cow = Cow.objects.get(id=cow_id)
        except Cow.DoesNotExist:
            return Response({"detail": "Cow not found."}, status=status.HTTP_404_NOT_FOUND)
        result = PredictionService.run_milk_forecast(cow)
        return Response(result)


class DiseasePredictionView(APIView):
    permission_classes = [IsVetOrAbove]

    @extend_schema(
        tags=["🤖 Predictions"],
        summary="Run disease risk detection (Random Forest)",
        description=(
            "Runs the **Random Forest** disease risk classifier. "
            "Returns probability scores for 7 disease types:\n"
            "- **FMD** (Foot and Mouth Disease) — threshold 0.60\n"
            "- **ECF** (East Coast Fever) — threshold 0.55\n"
            "- **Mastitis** — threshold 0.50\n"
            "- **Respiratory Disease** — threshold 0.55\n"
            "- **Nutritional Deficiency** — threshold 0.65\n"
            "- **Brucellosis** — threshold 0.70 ⚠️ quarantine required\n"
            "- **LSD** (Lumpy Skin Disease) — threshold 0.60\n\n"
            "FMD and Brucellosis trigger `emergency: true`."
        ),
        request=inline_serializer("DiseaseRequest", fields={
            "cow_id":             s.IntegerField(),
            "breed":              s.CharField(),
            "age_months":         s.IntegerField(),
            "body_temperature_c": s.FloatField(),
            "weight_kg":          s.FloatField(),
            "feeding_type":       s.ChoiceField(choices=["Poor","Adequate","Good"]),
            "water_access":       s.BooleanField(required=False),
            "fever":              s.BooleanField(required=False),
            "lameness":           s.BooleanField(required=False),
            "nasal_discharge":    s.BooleanField(required=False),
            "skin_lesions":       s.BooleanField(required=False),
            "reduced_appetite":   s.BooleanField(required=False),
            "weight_loss":        s.BooleanField(required=False),
            "swollen_lymph_nodes":s.BooleanField(required=False),
            "diarrhea":           s.BooleanField(required=False),
            "labored_breathing":  s.BooleanField(required=False),
            "mastitis_signs":     s.BooleanField(required=False),
        }),
        responses={
            200: OpenApiResponse(
                description="Disease probabilities",
                examples=[OpenApiExample(
                    "FMD detected",
                    value={
                        "cow_id": 12, "top_prediction": "FMD", "top_probability": 0.9708,
                        "all_disease_probabilities": {
                            "FMD": 0.9708, "ECF": 0.012, "Mastitis": 0.008,
                            "Respiratory": 0.005, "Nutritional_Deficiency": 0.003,
                            "Brucellosis": 0.001, "LSD": 0.001,
                        },
                        "triggered_alerts": [{
                            "disease": "FMD", "probability": 0.9708, "threshold_used": 0.60,
                            "alert_triggered": True,
                            "recommended_action": "Isolate cow immediately. Notify RAB and district vet.",
                        }],
                        "emergency": True, "total_symptoms_observed": 4,
                        "alert_triggered": True,
                        "alert_severity": "CRITICAL",
                        "model_version": "v1.0.0",
                    },
                )],
            )
        },
        examples=[
            OpenApiExample(
                "Cow with FMD symptoms",
                value={
                    "cow_id": 12, "breed": "Ankole_Cross", "age_months": 48,
                    "body_temperature_c": 40.5, "weight_kg": 310.0,
                    "feeding_type": "Adequate", "water_access": True,
                    "fever": True, "lameness": True, "nasal_discharge": True,
                    "reduced_appetite": True,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Cow with mastitis signs",
                value={
                    "cow_id": 9, "breed": "Friesian", "age_months": 36,
                    "body_temperature_c": 39.2, "weight_kg": 420.0,
                    "feeding_type": "Good", "water_access": True,
                    "mastitis_signs": True, "reduced_appetite": True,
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        cow_id = request.data.get("cow_id")
        try:
            cow = Cow.objects.get(id=cow_id)
        except Cow.DoesNotExist:
            return Response({"detail": "Cow not found."}, status=status.HTTP_404_NOT_FOUND)
        result = PredictionService.run_disease_check(cow, request.data)
        return Response(result)


class BirthPredictionView(APIView):
    permission_classes = [IsCellLeaderOrAbove]

    @extend_schema(
        tags=["🤖 Predictions"],
        summary="Run birth success probability (Logistic Regression)",
        description=(
            "Predicts the probability of a **successful calving outcome** for a pregnant cow. "
            "Score ≥ 0.86 auto-flags the calf as eligible for the Pass-On program."
        ),
        request=inline_serializer("BirthRequest", fields={
            "cow_id":                    s.IntegerField(),
            "breed":                     s.CharField(),
            "cow_age_months":            s.IntegerField(),
            "lactation_number":          s.IntegerField(),
            "initial_health_status":     s.ChoiceField(choices=["Poor","Fair","Good","Excellent"]),
            "feeding_type":              s.ChoiceField(choices=["Poor","Adequate","Good"]),
            "water_access":              s.BooleanField(required=False),
            "disease_cases_last_180d":   s.IntegerField(required=False),
            "vet_access":                s.BooleanField(required=False),
            "avg_temperature_last_trim": s.FloatField(required=False),
            "days_until_expected_birth": s.IntegerField(required=False),
        }),
        responses={
            200: OpenApiResponse(
                description="Birth probability",
                examples=[
                    OpenApiExample(
                        "Excellent prognosis",
                        value={
                            "cow_id": 5, "birth_success_probability": 0.923,
                            "prognosis_label": "Excellent",
                            "pass_on_eligible": True,
                            "recommended_action": "✅ Auto-flag calf for Pass-On program after birth.",
                            "alert_triggered": False,
                            "alert_severity": "NONE",
                            "model_version": "v1.0.0",
                        },
                    ),
                    OpenApiExample(
                        "High risk birth",
                        value={
                            "cow_id": 18, "birth_success_probability": 0.31,
                            "prognosis_label": "High Risk",
                            "pass_on_eligible": False,
                            "recommended_action": "🔴 Urgent pre-birth vet exam required. Alert cell leader.",
                            "alert_triggered": True,
                            "alert_severity": "CRITICAL",
                            "model_version": "v1.0.0",
                        },
                    ),
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Healthy first-time calver",
                value={
                    "cow_id": 5, "breed": "Friesian", "cow_age_months": 36,
                    "lactation_number": 1, "initial_health_status": "Good",
                    "feeding_type": "Good", "water_access": True,
                    "vet_access": True, "days_until_expected_birth": 14,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Older cow, poor conditions",
                value={
                    "cow_id": 18, "breed": "Ankole", "cow_age_months": 84,
                    "lactation_number": 6, "initial_health_status": "Poor",
                    "feeding_type": "Poor", "water_access": False,
                    "disease_cases_last_180d": 4, "vet_access": False,
                    "avg_temperature_last_trim": 32.0, "days_until_expected_birth": 5,
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        cow_id = request.data.get("cow_id")
        try:
            cow = Cow.objects.get(id=cow_id)
        except Cow.DoesNotExist:
            return Response({"detail": "Cow not found."}, status=status.HTTP_404_NOT_FOUND)
        result = PredictionService.run_birth_check(cow, request.data)
        return Response(result)


class PredictionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsCellLeaderOrAbove]
    serializer_class   = PredictionLogSerializer
    queryset           = PredictionLog.objects.select_related("cow", "model").all()

    @extend_schema(tags=["🤖 Predictions"], summary="List prediction logs", description="Returns prediction audit logs. Filter by `?cow_id=` to see logs for a specific cow.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=["🤖 Predictions"], summary="Get prediction log detail")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        cow_id = self.request.query_params.get("cow_id")
        if cow_id:
            qs = qs.filter(cow_id=cow_id)
        return qs


class AIModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class   = AIModelSerializer
    queryset           = AIModel.objects.all()

    @extend_schema(tags=["🤖 Predictions"], summary="List AI model versions", description="List all registered ML model versions (deployed and historical).")
    def list(self, request, *args, **kwargs): return super().list(request, *args, **kwargs)

    @extend_schema(tags=["🤖 Predictions"], summary="Get AI model details")
    def retrieve(self, request, *args, **kwargs): return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["🤖 Predictions"],
        summary="Deploy a model version",
        description="Set this model version as the active deployed model. Automatically deactivates the current deployed version of the same type.",
        request=None,
        responses={200: OpenApiResponse(description="Model deployed")},
    )
    @action(detail=True, methods=["post"])
    def deploy(self, request, pk=None):
        model = self.get_object()
        AIModel.objects.filter(model_type=model.model_type, is_deployed=True).update(is_deployed=False)
        model.is_deployed = True
        model.save(update_fields=["is_deployed"])
        return Response({"detail": f"{model} deployed."})

    @extend_schema(
        tags=["🤖 Predictions"],
        summary="View deployed model performance",
        description="Returns accuracy metrics (R², MAE, RMSE) for all currently deployed models.",
        responses={200: AIModelSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def performance(self, request):
        models = AIModel.objects.filter(is_deployed=True)
        return Response(AIModelSerializer(models, many=True).data)

    @extend_schema(
        tags=["🤖 Predictions"],
        summary="Trigger model retrain",
        description="Queues a full ML model retrain pipeline on the ML service. Runs asynchronously via Celery.",
        request=None,
        responses={202: OpenApiResponse(description="Retrain queued")},
    )
    @action(detail=False, methods=["post"])
    def retrain(self, request):
        from .tasks import trigger_model_retrain
        trigger_model_retrain.delay()
        return Response({"detail": "Retrain pipeline queued."}, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        tags=["🤖 Predictions"],
        summary="ML service health check",
        description="Checks if the Girinka ML FastAPI service is reachable and all 4 models are loaded.",
        responses={
            200: OpenApiResponse(description="ML service status", examples=[OpenApiExample(
                "All healthy",
                value={"status": "ok", "models": {"catboost": True, "lstm": True, "random_forest": True, "logistic": True}},
            )]),
            503: OpenApiResponse(description="ML service unreachable"),
        },
    )
    @action(detail=False, methods=["get"])
    def health_check(self, request):
        try:
            result = ml_client.health()
            return Response(result)
        except Exception as e:
            return Response({"status": "down", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
