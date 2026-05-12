from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="features.predictions.tasks.run_daily_risk_assessment")
def run_daily_risk_assessment():
    from features.cows.models import Cow
    from .services import PredictionService
    cows = Cow.objects.filter(is_alive=True).select_related("beneficiary","district")
    success, failed = 0, 0
    for cow in cows:
        try:
            PredictionService.run_mortality_check(cow)
            success += 1
        except Exception as e:
            logger.warning(f"Risk check failed for cow {cow.id}: {e}")
            failed += 1
    logger.info(f"Risk assessment: {success} success, {failed} failed.")
    return {"success": success, "failed": failed}


@shared_task(name="features.predictions.tasks.monthly_model_retrain")
def monthly_model_retrain():
    """Trigger full retraining pipeline on the ML service."""
    import httpx
    from django.conf import settings
    try:
        r = httpx.post(f"{settings.ML_SERVICE_URL}/retrain", timeout=300)
        logger.info(f"Retrain triggered: {r.status_code}")
        return r.json()
    except Exception as e:
        logger.error(f"Retrain failed: {e}")
        return {"error": str(e)}


@shared_task(name="features.predictions.tasks.archive_old_predictions")
def archive_old_predictions():
    from django.utils import timezone
    from datetime import timedelta
    from .models import PredictionLog
    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = PredictionLog.objects.filter(predicted_at__lt=cutoff).delete()
    logger.info(f"Archived {deleted} old prediction logs.")
    return deleted


@shared_task(name="features.predictions.tasks.trigger_model_retrain")
def trigger_model_retrain():
    return monthly_model_retrain()
