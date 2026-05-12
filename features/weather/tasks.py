
from celery import shared_task
import httpx, logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(name="features.weather.tasks.fetch_daily_weather")
def fetch_daily_weather():
    from features.districts.models import District
    from features.weather.models import WeatherData
    districts = District.objects.filter(latitude__isnull=False, longitude__isnull=False)
    created = 0
    for d in districts:
        try:
            r = httpx.get(settings.OPENMETEO_BASE_URL, params={
                "latitude": d.latitude, "longitude": d.longitude,
                "daily": "temperature_2m_max,precipitation_sum,relative_humidity_2m_max",
                "timezone": "Africa/Kigali", "forecast_days": 7,
            }, timeout=15)
            data = r.json()
            daily = data.get("daily", {})
            for i, date_str in enumerate(daily.get("time", [])):
                WeatherData.objects.update_or_create(
                    district=d, forecast_day=i, reading_time=f"{date_str}T00:00:00+02:00",
                    defaults={
                        "temperature": (daily.get("temperature_2m_max") or [None])[i],
                        "rainfall": (daily.get("precipitation_sum") or [None])[i],
                        "humidity": (daily.get("relative_humidity_2m_max") or [None])[i],
                        "data_source": "OpenMeteo",
                    }
                )
                created += 1
        except Exception as e:
            logger.error(f"Weather fetch failed for {d}: {e}")
    logger.info(f"Weather fetch complete: {created} records.")
    return created
