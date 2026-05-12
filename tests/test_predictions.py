"""Prediction endpoint tests."""
import pytest
from unittest.mock import patch, MagicMock
from features.cows.models import HealthStatus


ML_MORTALITY_RESPONSE = {
    "cow_id": 1,
    "mortality_risk_score": 0.72,
    "risk_level": "HIGH",
    "alert_triggered": True,
    "alert_severity": "URGENT",
    "sms_required": False,
    "sms_recipients": [],
    "recommended_action": "🔶 Urgent vet consultation within 24 hours.",
    "model_version": "v1.0.0",
}

ML_MILK_RESPONSE = {
    "cow_id": 1,
    "forecast_days": 7,
    "forecasts": [{"day": i, "predicted_yield_litres": 10.5, "confidence": "medium"} for i in range(1, 8)],
    "avg_predicted_yield_litres": 10.5,
    "total_predicted_litres": 73.5,
    "data_quality": "sufficient",
    "note": "High confidence forecast.",
    "model_version": "v1.0.0",
}


@pytest.mark.django_db
class TestMortalityPrediction:

    @patch("features.predictions.ml_client.ml_client.predict_mortality", return_value=ML_MORTALITY_RESPONSE)
    def test_mortality_check_updates_cow(self, mock_ml, cow):
        from features.predictions.services import PredictionService
        result = PredictionService.run_mortality_check(cow)
        assert result["mortality_risk_score"] == 0.72
        cow.refresh_from_db()
        assert cow.mortality_risk_score == 0.72
        assert cow.health_status == HealthStatus.HIGH_RISK

    @patch("features.predictions.ml_client.ml_client.predict_mortality", return_value=ML_MORTALITY_RESPONSE)
    def test_mortality_creates_alert(self, mock_ml, cow):
        from features.predictions.services import PredictionService
        from features.alerts.models import Alert
        with patch("features.predictions.services.PredictionService._send_alert_email"):
            PredictionService.run_mortality_check(cow)
        assert Alert.objects.filter(cow=cow, alert_type="MORTALITY_RISK").exists()

    @patch("features.predictions.ml_client.ml_client.predict_mortality", side_effect=Exception("ML down"))
    def test_mortality_handles_ml_error(self, mock_ml, cow):
        from features.predictions.services import PredictionService
        result = PredictionService.run_mortality_check(cow)
        assert "error" in result

    @patch("features.predictions.ml_client.ml_client.predict_mortality", return_value=ML_MORTALITY_RESPONSE)
    def test_mortality_endpoint(self, mock_ml, auth_cl, cow, cell_leader_user, district):
        cell_leader_user.district = district
        cell_leader_user.save()
        with patch("features.predictions.services.PredictionService._send_alert_email"):
            r = auth_cl.post("/api/v1/predictions/mortality/", {"cow_id": cow.id})
        assert r.status_code == 200
        assert r.data["data"]["risk_level"] == "HIGH"

    def test_mortality_endpoint_requires_cl(self, auth_farmer, cow):
        r = auth_farmer.post("/api/v1/predictions/mortality/", {"cow_id": cow.id})
        assert r.status_code == 403


@pytest.mark.django_db
class TestMilkForecast:

    def test_insufficient_data_raises_error(self, cow):
        from features.predictions.services import PredictionService
        from shared.exceptions import InsufficientMilkDataError
        with pytest.raises(InsufficientMilkDataError):
            PredictionService.run_milk_forecast(cow)

    @patch("features.predictions.ml_client.ml_client.predict_milk", return_value=ML_MILK_RESPONSE)
    def test_milk_forecast_with_enough_data(self, mock_ml, cow):
        from features.milk.models import MilkProduction
        from features.predictions.services import PredictionService
        from datetime import date, timedelta
        for i in range(10):
            MilkProduction.objects.create(
                cow=cow,
                daily_yield=12.0 + i * 0.1,
                morning_yield=6.6,
                evening_yield=5.4,
                collection_date=date.today() - timedelta(days=i),
            )
        result = PredictionService.run_milk_forecast(cow)
        assert result["avg_predicted_yield_litres"] == 10.5
