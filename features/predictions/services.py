"""
Prediction service — calls ML microservice, saves results, sends email alerts.
No SMS. Emails sent via Resend through features.notifications.utils.
"""
import logging
from datetime import date
from django.utils import timezone
from features.cows.models import Cow, HealthStatus
from features.alerts.models import Alert, AlertSeverity, AlertType, NotificationLog
from features.notifications.models import Notification
from .ml_client import ml_client
from .models import PredictionLog, PredictionType, AIModel, ModelType

logger = logging.getLogger(__name__)


def _get_deployed_model(model_type: str):
    return AIModel.objects.filter(model_type=model_type, is_deployed=True).first()


class PredictionService:

    @staticmethod
    def run_mortality_check(cow: Cow) -> dict:
        district     = cow.district
        latest_health = cow.health_records.order_by("-date_recorded").first()
        days_since_vet = (
            (date.today() - latest_health.date_recorded.date()).days
            if latest_health else 90
        )

        payload = {
            "cow_id":                  cow.id,
            "breed":                   cow.breed,
            "district":                district.district_name,
            "ubudehe_category":        cow.beneficiary.ubudehe_category,
            "initial_health_status":   "Good",
            "feeding_type":            "Adequate",
            "water_source":            "Borehole",
            "disease_cases":           cow.health_records.count(),
            "vet_coverage_rate":       0.6,
            "poverty_rate":            0.4,
            "years_in_program":        round((date.today() - cow.created_at.date()).days / 365.25, 2),
            "reproduction_count":      cow.lactation_number,
            "lactation_number":        cow.lactation_number,
            "days_since_last_vet_visit": days_since_vet,
            "avg_temperature_c":       20.0,
            "avg_rainfall_mm":         1100.0,
        }

        try:
            result = ml_client.predict_mortality(payload)
        except Exception as e:
            logger.error(f"Mortality prediction failed for cow {cow.id}: {e}")
            return {"error": str(e)}

        score = result.get("mortality_risk_score", 0.0)
        level = result.get("risk_level", "LOW")

        # Update cow record
        status_map = {
            "EMERGENCY":  HealthStatus.EMERGENCY,
            "VERY_HIGH":  HealthStatus.CRITICAL,
            "HIGH":       HealthStatus.HIGH_RISK,
            "MEDIUM":     HealthStatus.AT_RISK,
            "MEDIUM_LOW": HealthStatus.AT_RISK,
            "LOW":        HealthStatus.HEALTHY,
        }
        cow.mortality_risk_score = score
        cow.health_status = status_map.get(level, HealthStatus.HEALTHY)
        cow.save(update_fields=["mortality_risk_score", "health_status"])

        # Log prediction
        model = _get_deployed_model(ModelType.CATBOOST)
        PredictionLog.objects.create(
            cow=cow, model=model,
            prediction_type=PredictionType.MORTALITY_RISK,
            input_features=payload,
            output_values=result,
            confidence_score=score,
        )

        # Create alert if triggered
        if result.get("alert_triggered"):
            alert = Alert.objects.create(
                cow=cow,
                model=model,
                beneficiary=cow.beneficiary,
                alert_type=AlertType.MORTALITY_RISK,
                severity=result.get("alert_severity", AlertSeverity.WARNING),
                risk_score=score,
                message=f"Mortality risk score: {score:.2f} — {level}",
                recommendation=result.get("recommended_action", ""),
            )
            
            # Create in-app notification for farmer
            PredictionService._create_mortality_notifications(alert, cow, score, level)
            
            # Send email alert (no SMS)
            if score >= 0.60:
                PredictionService._send_alert_email(alert)

        return result

    @staticmethod
    def run_milk_forecast(cow: Cow) -> dict:
        records = list(cow.milk_records.order_by("-collection_date")[:15])
        if len(records) < 7:
            from shared.exceptions import InsufficientMilkDataError
            raise InsufficientMilkDataError()

        payload_records = []
        for r in reversed(records):
            payload_records.append({
                "daily_yield":   r.daily_yield,
                "morning_yield": r.morning_yield or round(r.daily_yield * 0.55, 2),
                "evening_yield": r.evening_yield or round(r.daily_yield * 0.45, 2),
                "feed_amount":   r.feed_amount or 6.0,
                "water_intake":  r.water_intake or 35.0,
                "temperature":   20.0,
                "rainfall":      2.0,
                "health_status": "Healthy",
                "day_of_week":   r.collection_date.weekday(),
                "month":         r.collection_date.month,
                "lactation_day": cow.days_in_milk or 90,
            })

        try:
            result = ml_client.predict_milk({"cow_id": cow.id, "records": payload_records})
        except Exception as e:
            logger.error(f"Milk forecast failed for cow {cow.id}: {e}")
            return {"error": str(e)}

        avg = result.get("avg_predicted_yield_litres", 0)
        if avg < 5.0:
            alert = Alert.objects.create(
                cow=cow,
                beneficiary=cow.beneficiary,
                alert_type=AlertType.LOW_MILK,
                severity=AlertSeverity.WARNING,
                message=f"7-day avg milk forecast: {avg:.2f} L/day — below 5L threshold.",
                recommendation="Review feed quantity and consult your vet.",
            )
            
            # Create in-app notification for farmer
            PredictionService._create_milk_notifications(alert, cow, avg)
            
            # Send email alert
            PredictionService._send_alert_email(alert)

        return result

    @staticmethod
    def run_disease_check(cow: Cow, payload: dict) -> dict:
        """Run disease prediction and create alerts for triggered diseases."""
        try:
            result = ml_client.predict_disease(payload)
        except Exception as e:
            logger.error(f"Disease prediction failed for cow {cow.id}: {e}")
            return {"error": str(e)}

        # Log prediction
        model = _get_deployed_model(ModelType.RANDOM_FOREST)
        PredictionLog.objects.create(
            cow=cow,
            model=model,
            prediction_type=PredictionType.DISEASE_RISK,
            input_features=payload,
            output_values=result,
            confidence_score=result.get("top_probability", 0.0),
        )

        # Process triggered alerts
        triggered_alerts = result.get("triggered_alerts", [])
        emergency = result.get("emergency", False)
        alert_created = False

        for alert_data in triggered_alerts:
            if not alert_data.get("alert_triggered"):
                continue

            disease = alert_data.get("disease", "Unknown")
            probability = alert_data.get("probability", 0.0)
            recommended_action = alert_data.get("recommended_action", "")

            # Determine severity
            if emergency:
                severity = AlertSeverity.CRITICAL
            elif probability >= 0.75:
                severity = AlertSeverity.URGENT
            elif probability >= 0.50:
                severity = AlertSeverity.WARNING
            else:
                severity = AlertSeverity.INFO

            # Create alert
            alert = Alert.objects.create(
                cow=cow,
                model=model,
                beneficiary=cow.beneficiary,
                alert_type=AlertType.DISEASE_OUTBREAK,
                severity=severity,
                risk_score=probability,
                message=f"Disease prediction: {disease} ({round(probability * 100)}% probability)",
                recommendation=recommended_action,
            )
            alert_created = True

            # Create in-app notification for vet and cell leader
            PredictionService._create_disease_notifications(alert, cow, disease, probability)

            # Send email if emergency
            if emergency:
                PredictionService._send_alert_email(alert)

        # Add alert metadata to response
        if alert_created:
            result["alert_triggered"] = True
            result["alert_severity"] = severity
        else:
            result["alert_triggered"] = False
            result["alert_severity"] = "NONE"

        return result

    @staticmethod
    def run_birth_check(cow: Cow, payload: dict) -> dict:
        """Run birth prediction and create alerts for high-risk births."""
        try:
            result = ml_client.predict_birth(payload)
        except Exception as e:
            logger.error(f"Birth prediction failed for cow {cow.id}: {e}")
            return {"error": str(e)}

        # Log prediction
        model = _get_deployed_model(ModelType.LOGISTIC_REGRESSION)
        PredictionLog.objects.create(
            cow=cow,
            model=model,
            prediction_type=PredictionType.BIRTH_PROBABILITY,
            input_features=payload,
            output_values=result,
            confidence_score=result.get("birth_success_probability", 0.0),
        )

        probability = result.get("birth_success_probability", 0.0)
        prognosis = result.get("prognosis_label", "Unknown")
        recommended_action = result.get("recommended_action", "")

        # Create alert for high-risk births (probability < 0.50)
        alert_created = False
        if probability < 0.50:
            # Determine severity based on risk level
            if probability < 0.30:
                severity = AlertSeverity.CRITICAL
            elif probability < 0.40:
                severity = AlertSeverity.URGENT
            else:
                severity = AlertSeverity.WARNING

            alert = Alert.objects.create(
                cow=cow,
                model=model,
                beneficiary=cow.beneficiary,
                alert_type=AlertType.PASS_ON_DUE,  # Using PASS_ON_DUE as it's birth-related
                severity=severity,
                risk_score=1.0 - probability,  # Invert to show risk, not success
                message=f"High-risk birth detected: {prognosis} ({round(probability * 100)}% success probability)",
                recommendation=recommended_action,
            )
            alert_created = True

            # Create in-app notification for cell leader
            PredictionService._create_birth_notifications(alert, cow, prognosis, probability)

            # Send email for critical cases
            if probability < 0.40:
                PredictionService._send_alert_email(alert)

        # Add alert metadata to response
        if alert_created:
            result["alert_triggered"] = True
            result["alert_severity"] = severity
        else:
            result["alert_triggered"] = False
            result["alert_severity"] = "NONE"

        return result

    @staticmethod
    def _create_mortality_notifications(alert: Alert, cow: Cow, score: float, level: str) -> None:
        """Create in-app notifications for mortality risk alerts."""
        # Notify farmer
        if cow.beneficiary.user:
            severity_emoji = {
                "EMERGENCY": "🚨",
                "VERY_HIGH": "⚠️",
                "HIGH": "⚠️",
                "MEDIUM": "ℹ️",
                "LOW": "✅"
            }
            emoji = severity_emoji.get(level, "⚠️")
            
            Notification.objects.create(
                user=cow.beneficiary.user,
                alert=alert,
                title=f"{emoji} Mortality Risk Alert",
                message=f"Your cow {cow.tag_number} has a {round(score * 100)}% mortality risk ({level}). {alert.recommendation}",
            )
        
        # Notify cell leader if high risk
        if score >= 0.60:
            from features.users.models import User
            cell_leaders = User.objects.filter(
                role="CELL_LEADER",
                district=cow.district,
                is_active=True
            )
            for leader in cell_leaders:
                Notification.objects.create(
                    user=leader,
                    alert=alert,
                    title=f"🚨 High Mortality Risk in Your District",
                    message=f"Cow {cow.tag_number} (Owner: {cow.beneficiary.full_name}) has {round(score * 100)}% mortality risk. Immediate action required.",
                )

    @staticmethod
    def _create_milk_notifications(alert: Alert, cow: Cow, avg_yield: float) -> None:
        """Create in-app notifications for low milk production alerts."""
        # Notify farmer
        if cow.beneficiary.user:
            Notification.objects.create(
                user=cow.beneficiary.user,
                alert=alert,
                title=f"🥛 Low Milk Production Alert",
                message=f"Your cow {cow.tag_number} is predicted to produce only {avg_yield:.1f}L/day over the next 7 days. {alert.recommendation}",
            )
        
        # Notify cell leader
        from features.users.models import User
        cell_leaders = User.objects.filter(
            role="CELL_LEADER",
            district=cow.district,
            is_active=True
        )
        for leader in cell_leaders:
            Notification.objects.create(
                user=leader,
                alert=alert,
                title=f"📉 Low Milk Production in Your District",
                message=f"Cow {cow.tag_number} (Owner: {cow.beneficiary.full_name}) showing low milk forecast: {avg_yield:.1f}L/day.",
            )

    @staticmethod
    def _create_disease_notifications(alert: Alert, cow: Cow, disease: str, probability: float) -> None:
        """Create in-app notifications for vet and cell leader."""
        district = cow.district
        
        # Notify district vet
        vets = district.vets.filter(is_active=True)
        for vet in vets:
            Notification.objects.create(
                user=vet.user,
                alert=alert,
                title=f"Disease Alert: {disease}",
                message=f"Cow {cow.tag_number} shows {round(probability * 100)}% probability of {disease}. Immediate attention required.",
            )

        # Notify cell leader (beneficiary's user if they're a cell leader, or district cell leaders)
        if cow.beneficiary.user and cow.beneficiary.user.role == "CELL_LEADER":
            Notification.objects.create(
                user=cow.beneficiary.user,
                alert=alert,
                title=f"Disease Alert: {disease}",
                message=f"Cow {cow.tag_number} requires veterinary attention for suspected {disease}.",
            )

    @staticmethod
    def _create_birth_notifications(alert: Alert, cow: Cow, prognosis: str, probability: float) -> None:
        """Create in-app notifications for cell leader."""
        # Notify cell leader
        if cow.beneficiary.user and cow.beneficiary.user.role == "CELL_LEADER":
            Notification.objects.create(
                user=cow.beneficiary.user,
                alert=alert,
                title=f"High-Risk Birth: {prognosis}",
                message=f"Cow {cow.tag_number} has {round(probability * 100)}% birth success probability. Pre-birth vet exam recommended.",
            )

    @staticmethod
    def _send_alert_email(alert: Alert) -> None:
        """Send alert email to farmer via Resend. No SMS."""
        from features.notifications.utils import send_alert_email
        farmer = alert.beneficiary
        email  = farmer.user.email if farmer.user else None
        if not email:
            logger.warning(f"No email for beneficiary {farmer.id} — alert email skipped.")
            return
        try:
            send_alert_email(
                to=email,
                farmer_name=farmer.full_name,
                cow_tag=alert.cow.tag_number,
                alert_type=alert.alert_type,
                severity=alert.severity,
                message=alert.message or "",
                recommendation=alert.recommendation or "",
            )
            alert.sent_via_sms = False   # field kept for schema compat
            alert.save(update_fields=["sent_via_sms"])
            logger.info(f"Alert email sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Alert email failed for alert {alert.id}: {e}")
