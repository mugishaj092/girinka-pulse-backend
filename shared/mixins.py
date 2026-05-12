"""Reusable ViewSet mixins."""
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status


class CachedListMixin:
    """Cache the list response for a configurable TTL."""
    cache_key_prefix = "list"
    cache_ttl = 300  # 5 minutes

    def list(self, request, *args, **kwargs):
        cache_key = f"{self.cache_key_prefix}:{request.user.id}:{request.query_params}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, self.cache_ttl)
        return response


class AuditLogMixin:
    """Auto-create audit log entries on create/update/delete."""
    def perform_create(self, serializer):
        instance = serializer.save()
        self._log("CREATE", instance)
        return instance

    def perform_update(self, serializer):
        old = serializer.instance.__dict__.copy()
        instance = serializer.save()
        self._log("UPDATE", instance, old)
        return instance

    def perform_destroy(self, instance):
        self._log("DELETE", instance)
        instance.delete()

    def _log(self, action, instance, old_values=None):
        try:
            from features.users.models import AuditLog
            AuditLog.objects.create(
                user=self.request.user,
                action=action,
                resource_type=instance.__class__.__name__,
                resource_id=instance.pk,
                old_values=old_values,
                new_values=instance.__dict__,
                ip_address=self.request.META.get("REMOTE_ADDR"),
                user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
            )
        except Exception:
            pass
