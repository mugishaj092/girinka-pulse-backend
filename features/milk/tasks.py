
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="features.milk.tasks.run_daily_milk_forecasts")
def run_daily_milk_forecasts():
    from features.cows.models import Cow
    from features.predictions.services import PredictionService
    cows = Cow.objects.filter(is_alive=True, milk_records__isnull=False).distinct()
    success, failed = 0, 0
    for cow in cows:
        try:
            if cow.milk_records.count() >= 7:
                PredictionService.run_milk_forecast(cow)
                success += 1
        except Exception as e:
            logger.warning(f"Milk forecast skipped for cow {cow.id}: {e}")
            failed += 1
    logger.info(f"Milk forecasts: {success} success, {failed} failed.")
    return {"success": success, "failed": failed}
