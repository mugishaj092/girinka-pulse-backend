Read `progress-tracker.md`, `architecture-context.md`, `api-context.md`, and `code-standards.md` before starting.

# 04 — Districts

Verify and complete the Districts module. Districts are the geographic foundation of the entire system — every beneficiary, cow, vet, and weather reading belongs to a district. This spec requires that spec `01-database-seed` has been run and all 30 districts are in the database.

---

## Endpoints

All under `/api/v1/districts/`.

---

### GET `/api/v1/districts/`

**Auth required:** Any authenticated user

**No pagination required** — there are exactly 30 districts and the full list should be returned in one response.

**Success `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "district_name": "Nyarugenge",
      "province": "Kigali",
      "sector": null,
      "cell": null,
      "latitude": -1.95,
      "longitude": 30.0588,
      "is_remote": false,
      "created_at": "2026-05-02T08:00:00+02:00"
    }
  ],
  "meta": { "count": 30, "next": null, "previous": null }
}
```

**Ordering:** Alphabetical by `district_name` (defined in `District.Meta.ordering`).

---

### POST `/api/v1/districts/`

**Auth required:** Admin only

**Request:**
```json
{
  "district_name": "TestDistrict",
  "province": "Eastern",
  "latitude": -1.9000,
  "longitude": 30.5000,
  "is_remote": false
}
```

**Success `201`:** Returns created district object.

**Error `403`:** For any non-admin user.

---

### GET `/api/v1/districts/{id}/`

**Auth required:** Any authenticated user

**Success `200`:** Returns single district object.

**Error `404`:** District does not exist.

---

### PATCH `/api/v1/districts/{id}/`

**Auth required:** Admin only

**Request** (all fields optional):
```json
{
  "sector": "Remera",
  "cell": "Bibare",
  "latitude": -1.9600,
  "longitude": 30.1100
}
```

**Success `200`:** Returns updated district object.

---

### DELETE `/api/v1/districts/{id}/`

**Auth required:** Admin only

**Behavior:** Hard delete — only allowed if no beneficiaries or cows are linked to this district.

If linked records exist, return:
```json
{
  "success": false,
  "message": "Cannot delete district with linked beneficiaries or cows.",
  "errors": { "detail": "This district has 42 cows and 18 beneficiaries attached." }
}
```

**Success `204`:** No content.

**Implementation note:** Override `destroy()` in `DistrictViewSet` to check for related records before deleting.

---

### GET `/api/v1/districts/{id}/stats/`

**Auth required:** Cell Leader and above

Returns live statistics computed from the database. Cached in memory for 1 hour using Django's cache framework. Cache key: `district_stats_{id}`.

**Success `200`:**
```json
{
  "success": true,
  "data": {
    "total_cows": 1240,
    "at_risk_cows": 87,
    "avg_milk": 11.3,
    "total_beneficiaries": 980
  }
}
```

**Fields:**
- `total_cows` — count of `Cow` objects where `district=this`, `is_alive=True`
- `at_risk_cows` — count of above where `health_status IN ['AT_RISK', 'HIGH_RISK', 'CRITICAL', 'EMERGENCY']`
- `avg_milk` — average `daily_yield` from `MilkProduction` for all cows in this district, last 30 days. Round to 2 decimal places. Return `0` if no records.
- `total_beneficiaries` — count of `Beneficiary` where `district=this`, `is_active=True`

**Implementation:**

```python
def get_stats(self):
    from django.db.models import Avg, Count
    from django.utils import timezone
    from datetime import timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    cows = self.cows.filter(is_alive=True)
    avg_milk = cows.filter(
        milk_records__collection_date__gte=thirty_days_ago.date()
    ).aggregate(avg=Avg("milk_records__daily_yield"))["avg"]
    return {
        "total_cows": cows.count(),
        "at_risk_cows": cows.filter(
            health_status__in=["AT_RISK","HIGH_RISK","CRITICAL","EMERGENCY"]
        ).count(),
        "avg_milk": round(avg_milk or 0, 2),
        "total_beneficiaries": self.beneficiaries.filter(is_active=True).count(),
    }
```

**Verify:**
- Cache is populated after first call
- Second call within 1 hour returns same value without DB query (add `print` statement to confirm)

---

### GET `/api/v1/districts/{id}/weather/`

**Auth required:** Any authenticated user

Returns the most recent `WeatherData` record for this district (`forecast_day=0`).

**Success `200`:**
```json
{
  "success": true,
  "data": {
    "id": 145,
    "district": 3,
    "district_name": "Gasabo",
    "temperature": 21.4,
    "humidity": 72.0,
    "rainfall": 2.5,
    "wind_speed": null,
    "reading_time": "2026-05-02T05:00:00+02:00",
    "data_source": "OpenMeteo",
    "forecast_day": 0
  }
}
```

**If no weather data exists yet:**
```json
{
  "success": true,
  "data": null,
  "message": "No weather data available for this district yet."
}
```

Do not return a 404 — return 200 with null data.

---

## Missing Pieces To Check For

### `District.get_stats()` method is implemented on the model

The stats computation must live on the model as a method, not in the view.

### Cache invalidation on cow/beneficiary mutations

When a new cow or beneficiary is registered in a district, the cache key `district_stats_{district_id}` must be invalidated. Add this to `signals.py` in both `cows` and `beneficiaries` modules:

```python
# features/cows/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Cow

@receiver(post_save, sender=Cow)
def invalidate_district_stats_cache(sender, instance, **kwargs):
    cache.delete(f"district_stats_{instance.district_id}")
```

Do the same in `features/beneficiaries/signals.py`.

Register signals in `apps.py` `ready()` method.

### `DistrictViewSet.destroy()` checks for linked records

Override `destroy()` to count related cows and beneficiaries before deleting.

---

## Completion Criteria

- [ ] `GET /districts/` returns all 30 districts ordered alphabetically
- [ ] `POST /districts/` creates district (Admin only, returns 403 for others)
- [ ] `GET /districts/{id}/` returns correct district
- [ ] `PATCH /districts/{id}/` updates fields
- [ ] `DELETE /districts/{id}/` blocked if cows or beneficiaries are linked
- [ ] `GET /districts/{id}/stats/` returns correct counts from database
- [ ] Stats are cached — second call within 1 hour does not hit the DB
- [ ] Cache is invalidated when a cow or beneficiary is added to the district
- [ ] `GET /districts/{id}/weather/` returns latest weather or null data
- [ ] `progress-tracker.md` updated
