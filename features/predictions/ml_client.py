
"""HTTP client for the Girinka ML FastAPI microservice."""
import httpx
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class MLClient:
    def __init__(self):
        self.base = settings.ML_SERVICE_URL
        self.timeout = settings.ML_SERVICE_TIMEOUT
        self.headers = {}
        if settings.ML_SERVICE_API_KEY:
            self.headers["X-API-Key"] = settings.ML_SERVICE_API_KEY

    def _post(self, endpoint: str, data: dict) -> dict:
        try:
            # Create SSL context that's more lenient for Render.com SSL certificates
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            r = httpx.post(
                f"{self.base}{endpoint}", 
                json=data, 
                timeout=self.timeout, 
                headers=self.headers,
                verify=ssl_context  # Use custom SSL context
            )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"ML service error {endpoint}: {e.response.status_code} {e.response.text}")
            raise Exception(f"ML service returned error: {e.response.status_code}")
        except httpx.ConnectError as e:
            logger.error(f"ML service connection failed {endpoint}: {e}")
            raise Exception(f"Cannot connect to ML service at {self.base}. Service may be down.")
        except httpx.TimeoutException as e:
            logger.error(f"ML service timeout {endpoint}: {e}")
            raise Exception(f"ML service request timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"ML service unexpected error {endpoint}: {type(e).__name__}: {e}")
            raise Exception(f"ML service error: {str(e)}")

    def predict_mortality(self, data: dict) -> dict:
        return self._post("/predict/mortality", data)

    def predict_milk(self, data: dict) -> dict:
        return self._post("/predict/milk", data)

    def predict_disease(self, data: dict) -> dict:
        return self._post("/predict/disease", data)

    def predict_birth(self, data: dict) -> dict:
        return self._post("/predict/birth", data)

    def health(self) -> dict:
        try:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            r = httpx.get(
                f"{self.base}/health", 
                timeout=10, 
                headers=self.headers,
                verify=ssl_context
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"ML service health check failed: {e}")
            return {"status": "error", "message": str(e)}


# Choose which client to use based on settings
if getattr(settings, 'USE_MOCK_ML_CLIENT', False):
    from .mock_ml_client import mock_ml_client
    ml_client = mock_ml_client
    logger.warning("🔶 Using MOCK ML Client - predictions are fake for testing!")
else:
    ml_client = MLClient()
    logger.info(f"✅ Using real ML Client at {settings.ML_SERVICE_URL}")
