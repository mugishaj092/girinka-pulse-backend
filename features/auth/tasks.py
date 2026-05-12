from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="features.auth.tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    """
    Clean up expired JWT outstanding tokens.
    No Redis needed — tokens are stored in PostgreSQL via simplejwt blacklist.
    """
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
    from django.utils import timezone
    deleted, _ = OutstandingToken.objects.filter(expires_at__lt=timezone.now()).delete()
    logger.info(f"Cleaned up {deleted} expired JWT tokens.")
    return {"deleted": deleted}
