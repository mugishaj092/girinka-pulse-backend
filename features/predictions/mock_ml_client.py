"""
Mock ML Client for Development/Testing
Use this when the real ML service is unavailable.
"""
import logging
import random

logger = logging.getLogger(__name__)


class MockMLClient:
    """Mock ML client that returns fake predictions for testing."""
    
    def __init__(self):
        logger.warning("Using MOCK ML Client - predictions are fake!")
    
    def predict_mortality(self, data: dict) -> dict:
        """Mock mortality prediction."""
        cow_id = data.get("cow_id", 0)
        # Generate consistent fake risk score based on cow_id
        random.seed(cow_id)
        risk_score = round(random.uniform(0.1, 0.9), 2)
        
        if risk_score >= 0.85:
            risk_level = "EMERGENCY"
            alert_severity = "CRITICAL"
        elif risk_score >= 0.70:
            risk_level = "VERY_HIGH"
            alert_severity = "URGENT"
        elif risk_score >= 0.60:
            risk_level = "HIGH"
            alert_severity = "URGENT"
        elif risk_score >= 0.40:
            risk_level = "MEDIUM"
            alert_severity = "WARNING"
        else:
            risk_level = "LOW"
            alert_severity = "INFO"
        
        alert_triggered = risk_score >= 0.40
        
        return {
            "cow_id": cow_id,
            "mortality_risk_score": risk_score,
            "risk_level": risk_level,
            "alert_triggered": alert_triggered,
            "alert_severity": alert_severity,
            "recommended_action": self._get_mortality_recommendation(risk_level),
            "model_version": "mock-v1.0",
            "prediction_timestamp": "2026-05-10T12:00:00Z"
        }
    
    def predict_milk(self, data: dict) -> dict:
        """Mock milk forecast."""
        cow_id = data.get("cow_id", 0)
        records = data.get("records", [])
        
        # Calculate average from recent records
        if records:
            recent_yields = [r.get("daily_yield", 10.0) for r in records[-7:]]
            avg_recent = sum(recent_yields) / len(recent_yields)
        else:
            avg_recent = 10.0
        
        # Generate 7-day forecast with slight variation
        random.seed(cow_id)
        forecast = []
        for day in range(1, 8):
            variation = random.uniform(-1.5, 1.5)
            predicted = max(0, round(avg_recent + variation, 2))
            forecast.append({
                "day": day,
                "predicted_yield_litres": predicted
            })
        
        avg_predicted = sum(f["predicted_yield_litres"] for f in forecast) / 7
        
        return {
            "cow_id": cow_id,
            "forecast_days": 7,
            "predictions": forecast,
            "avg_predicted_yield_litres": round(avg_predicted, 2),
            "model_version": "mock-lstm-v1.0",
            "prediction_timestamp": "2026-05-10T12:00:00Z"
        }
    
    def predict_disease(self, data: dict) -> dict:
        """Mock disease prediction."""
        cow_id = data.get("cow_id", 0)
        random.seed(cow_id)
        
        diseases = [
            "Foot and Mouth Disease",
            "East Coast Fever",
            "Mastitis",
            "Lumpy Skin Disease",
            "Brucellosis",
            "Anthrax",
            "Trypanosomiasis"
        ]
        
        # Generate probabilities
        probabilities = {}
        for disease in diseases:
            probabilities[disease] = round(random.uniform(0.05, 0.40), 2)
        
        # Pick top disease
        top_disease = max(probabilities, key=probabilities.get)
        top_probability = probabilities[top_disease]
        
        # Generate alerts for diseases with probability > 0.30
        triggered_alerts = []
        emergency = False
        
        for disease, prob in probabilities.items():
            if prob >= 0.30:
                alert_triggered = True
                if prob >= 0.35:
                    emergency = True
                triggered_alerts.append({
                    "disease": disease,
                    "probability": prob,
                    "alert_triggered": alert_triggered,
                    "recommended_action": f"Immediate veterinary examination for {disease}"
                })
        
        return {
            "cow_id": cow_id,
            "disease_probabilities": probabilities,
            "top_disease": top_disease,
            "top_probability": top_probability,
            "emergency": emergency,
            "triggered_alerts": triggered_alerts,
            "model_version": "mock-rf-v1.0",
            "prediction_timestamp": "2026-05-10T12:00:00Z"
        }
    
    def predict_birth(self, data: dict) -> dict:
        """Mock birth prediction."""
        cow_id = data.get("cow_id", 0)
        random.seed(cow_id)
        
        # Generate birth success probability
        probability = round(random.uniform(0.25, 0.95), 2)
        
        if probability >= 0.80:
            prognosis = "Excellent"
            risk_level = "LOW"
        elif probability >= 0.60:
            prognosis = "Good"
            risk_level = "MEDIUM"
        elif probability >= 0.40:
            prognosis = "Fair"
            risk_level = "HIGH"
        else:
            prognosis = "Poor"
            risk_level = "VERY_HIGH"
        
        return {
            "cow_id": cow_id,
            "birth_success_probability": probability,
            "prognosis_label": prognosis,
            "risk_level": risk_level,
            "recommended_action": self._get_birth_recommendation(risk_level),
            "model_version": "mock-lr-v1.0",
            "prediction_timestamp": "2026-05-10T12:00:00Z"
        }
    
    def health(self) -> dict:
        """Mock health check."""
        return {
            "status": "healthy",
            "service": "Mock ML Service",
            "models_loaded": 4,
            "models": {
                "mortality": "mock-catboost-v1.0",
                "milk": "mock-lstm-v1.0",
                "disease": "mock-rf-v1.0",
                "birth": "mock-lr-v1.0"
            }
        }
    
    @staticmethod
    def _get_mortality_recommendation(risk_level: str) -> str:
        recommendations = {
            "EMERGENCY": "🚨 EMERGENCY: Immediate veterinary intervention required. Cow's life at critical risk.",
            "VERY_HIGH": "🔴 CRITICAL: Urgent vet consultation within 12 hours. High mortality risk detected.",
            "HIGH": "🔶 URGENT: Schedule vet visit within 24-48 hours. Monitor cow closely.",
            "MEDIUM": "⚠️ WARNING: Schedule routine vet checkup within 1 week. Monitor health indicators.",
            "LOW": "✅ HEALTHY: Continue regular monitoring and feeding schedule."
        }
        return recommendations.get(risk_level, "Monitor cow health regularly.")
    
    @staticmethod
    def _get_birth_recommendation(risk_level: str) -> str:
        recommendations = {
            "LOW": "✅ Normal monitoring. Birth expected to proceed smoothly.",
            "MEDIUM": "⚠️ Schedule pre-birth vet examination. Prepare for potential complications.",
            "HIGH": "🔶 URGENT: Pre-birth vet exam required. Prepare emergency birthing assistance.",
            "VERY_HIGH": "🚨 CRITICAL: Immediate vet consultation. High-risk birth - prepare for C-section if needed."
        }
        return recommendations.get(risk_level, "Consult veterinarian before calving.")


# Create mock client instance
mock_ml_client = MockMLClient()
