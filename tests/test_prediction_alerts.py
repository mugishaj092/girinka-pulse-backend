"""
Test that disease and birth predictions create alerts correctly.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from features.cows.models import Cow
from features.alerts.models import Alert, AlertType, AlertSeverity
from features.notifications.models import Notification
from features.predictions.services import PredictionService


@pytest.mark.django_db
class TestDiseasePredictionAlerts:
    
    @patch('features.predictions.services.ml_client.predict_disease')
    def test_disease_prediction_creates_alert_on_emergency(self, mock_predict, cow, beneficiary):
        """Emergency disease (FMD) should create CRITICAL alert and send email."""
        mock_predict.return_value = {
            "cow_id": cow.id,
            "top_prediction": "FMD",
            "top_probability": 0.9708,
            "all_disease_probabilities": {
                "FMD": 0.9708,
                "ECF": 0.012,
                "Mastitis": 0.008,
            },
            "triggered_alerts": [{
                "disease": "FMD",
                "probability": 0.9708,
                "threshold_used": 0.60,
                "alert_triggered": True,
                "recommended_action": "Isolate cow immediately. Notify RAB and district vet.",
            }],
            "emergency": True,
            "total_symptoms_observed": 4,
            "model_version": "v1.0.0",
        }
        
        payload = {
            "cow_id": cow.id,
            "breed": "Ankole_Cross",
            "age_months": 48,
            "body_temperature_c": 40.5,
            "weight_kg": 310.0,
            "feeding_type": "Adequate",
            "fever": True,
            "lameness": True,
        }
        
        result = PredictionService.run_disease_check(cow, payload)
        
        assert result["alert_triggered"] is True
        assert result["alert_severity"] == AlertSeverity.CRITICAL
        
        # Check alert was created
        alert = Alert.objects.filter(cow=cow, alert_type=AlertType.DISEASE_OUTBREAK).first()
        assert alert is not None
        assert alert.severity == AlertSeverity.CRITICAL
        assert "FMD" in alert.message
        assert alert.risk_score == 0.9708
    
    @patch('features.predictions.services.ml_client.predict_disease')
    def test_disease_prediction_creates_urgent_alert_high_probability(self, mock_predict, cow):
        """High probability (≥0.75) should create URGENT alert."""
        mock_predict.return_value = {
            "cow_id": cow.id,
            "top_prediction": "Mastitis",
            "top_probability": 0.82,
            "triggered_alerts": [{
                "disease": "Mastitis",
                "probability": 0.82,
                "alert_triggered": True,
                "recommended_action": "Examine udder and start treatment.",
            }],
            "emergency": False,
        }
        
        result = PredictionService.run_disease_check(cow, {"cow_id": cow.id})
        
        assert result["alert_triggered"] is True
        assert result["alert_severity"] == AlertSeverity.URGENT
        
        alert = Alert.objects.filter(cow=cow, alert_type=AlertType.DISEASE_OUTBREAK).first()
        assert alert.severity == AlertSeverity.URGENT
    
    @patch('features.predictions.services.ml_client.predict_disease')
    def test_disease_prediction_no_alert_below_threshold(self, mock_predict, cow):
        """No triggered alerts should result in alert_triggered=False."""
        mock_predict.return_value = {
            "cow_id": cow.id,
            "top_prediction": "Healthy",
            "top_probability": 0.95,
            "triggered_alerts": [],
            "emergency": False,
        }
        
        result = PredictionService.run_disease_check(cow, {"cow_id": cow.id})
        
        assert result["alert_triggered"] is False
        assert result["alert_severity"] == "NONE"
        
        # No alert should be created
        alert_count = Alert.objects.filter(cow=cow, alert_type=AlertType.DISEASE_OUTBREAK).count()
        assert alert_count == 0


@pytest.mark.django_db
class TestBirthPredictionAlerts:
    
    @patch('features.predictions.services.ml_client.predict_birth')
    def test_birth_prediction_creates_critical_alert_very_low_probability(self, mock_predict, cow):
        """Very low birth success (<0.30) should create CRITICAL alert."""
        mock_predict.return_value = {
            "cow_id": cow.id,
            "birth_success_probability": 0.25,
            "prognosis_label": "Critical Risk",
            "pass_on_eligible": False,
            "recommended_action": "🔴 Emergency vet intervention required immediately.",
            "model_version": "v1.0.0",
        }
        
        result = PredictionService.run_birth_check(cow, {"cow_id": cow.id})
        
        assert result["alert_triggered"] is True
        assert result["alert_severity"] == AlertSeverity.CRITICAL
        
        alert = Alert.objects.filter(cow=cow, alert_type=AlertType.PASS_ON_DUE).first()
        assert alert is not None
        assert alert.severity == AlertSeverity.CRITICAL
        assert "25%" in alert.message
        assert alert.risk_score == 0.75  # Inverted (1.0 - 0.25)
    
    @patch('features.predictions.services.ml_client.predict_birth')
    def test_birth_prediction_creates_urgent_alert_low_probability(self, mock_predict, cow):
        """Low birth success (0.30-0.40) should create URGENT alert."""
        mock_predict.return_value = {
            "cow_id": cow.id,
            "birth_success_probability": 0.35,
            "prognosis_label": "High Risk",
            "pass_on_eligible": False,
            "recommended_action": "🔴 Urgent pre-birth vet exam required.",
            "model_version": "v1.0.0",
        }
        
        result = PredictionService.run_birth_check(cow, {"cow_id": cow.id})
        
        assert result["alert_triggered"] is True
        assert result["alert_severity"] == AlertSeverity.URGENT
        
        alert = Alert.objects.filter(cow=cow, alert_type=AlertType.PASS_ON_DUE).first()
        assert alert.severity == AlertSeverity.URGENT
    
    @patch('features.predictions.services.ml_client.predict_birth')
    def test_birth_prediction_creates_warning_alert_moderate_risk(self, mock_predict, cow):
        """Moderate risk (0.40-0.50) should create WARNING alert."""
        mock_predict.return_value = {
            "cow_id": cow.id,
            "birth_success_probability": 0.45,
            "prognosis_label": "Moderate Risk",
            "pass_on_eligible": False,
            "recommended_action": "Schedule pre-birth vet check.",
            "model_version": "v1.0.0",
        }
        
        result = PredictionService.run_birth_check(cow, {"cow_id": cow.id})
        
        assert result["alert_triggered"] is True
        assert result["alert_severity"] == AlertSeverity.WARNING
    
    @patch('features.predictions.services.ml_client.predict_birth')
    def test_birth_prediction_no_alert_high_success_probability(self, mock_predict, cow):
        """High success probability (≥0.50) should not create alert."""
        mock_predict.return_value = {
            "cow_id": cow.id,
            "birth_success_probability": 0.92,
            "prognosis_label": "Excellent",
            "pass_on_eligible": True,
            "recommended_action": "✅ Auto-flag calf for Pass-On program after birth.",
            "model_version": "v1.0.0",
        }
        
        result = PredictionService.run_birth_check(cow, {"cow_id": cow.id})
        
        assert result["alert_triggered"] is False
        assert result["alert_severity"] == "NONE"
        
        # No alert should be created
        alert_count = Alert.objects.filter(cow=cow, alert_type=AlertType.PASS_ON_DUE).count()
        assert alert_count == 0
