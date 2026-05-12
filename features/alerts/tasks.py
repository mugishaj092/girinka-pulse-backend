
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="features.alerts.tasks.escalate_unresolved_alerts")
def escalate_unresolved_alerts():
    from django.utils import timezone
    from datetime import timedelta
    from .models import Alert, AlertSeverity
    cutoff = timezone.now() - timedelta(hours=24)
    stale = Alert.objects.filter(is_resolved=False, alert_timestamp__lt=cutoff, severity=AlertSeverity.URGENT)
    count = stale.update(severity=AlertSeverity.CRITICAL)
    logger.info(f"Escalated {count} stale alerts to CRITICAL.")
    return count
