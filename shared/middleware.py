"""Custom middleware."""
import time
import logging

logger = logging.getLogger("girinka.requests")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = round((time.time() - start) * 1000, 2)
        logger.info(
            f"{request.method} {request.path} → {response.status_code} ({duration}ms)"
            f" user={getattr(request.user, 'id', 'anon')}"
        )
        return response
