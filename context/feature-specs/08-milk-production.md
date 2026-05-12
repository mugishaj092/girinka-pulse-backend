Read `progress-tracker.md`, `architecture-context.md`, `api-context.md`, and `code-standards.md` before starting.

# 08 — Milk Production

Verify and complete the Milk Production module. Daily milk records are the primary input to the LSTM forecast model. Accurate entry and validation are critical — bad data produces unreliable AI forecasts.

Requires: spec `06-cows` complete.

---

## Endpoints

All under `/api/v1/milk/`.

---

### GET `/api/v1/milk/`

**Auth required:** Any authenticated user (role-scoped)

**Data scoping:**
- `FARMER` → records for cows owned by their beneficiary
- `CELL_LEADER` / `VETERINARIAN` / `DISTRICT_LEADER` → records for cows in their district
- `ADMIN` → all records

**Query parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `cow` | integer | Filter by cow ID |
| `date_after` | date | Records from this date |
| `date_before` | date | Records up to this date |
| `page` | integer | Page number |

**Success `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 204,
      "cow": 42,
      "cow_tag": "RW-GAS-2026-001",
      "collection_date": "2026-05-02",
      "morning_yield": 6.8,
      "evening_yield": 5.7,
      "daily_yield": 12.5,
      "feed_amount": 6.0,
      "water_intake": 35.0,
      "lstm_forecast": null,
      "notes": "Cow was calm during milking.",
      "created_at": "2026-05-02T18:00:00+02:00"
    }
  ]
}
```

---

### POST `/api/v1/milk/`

**Auth required:** Farmer, Cell Leader

**Request:**
```json
{
  "cow": 42,
  "collection_date": "2026-05-02",
  "morning_yield": 6.8,
  "evening_yield": 5.7,
  "daily_yield": 12.5,
  "feed_amount": 6.0,
  "water_intake": 35.0,
  "notes": "Cow was calm during milking."
}
```

**Required fields:** `cow`, `collection_date`, `daily_yield`

**Optional fields:** `morning_yield`, `evening_yield`, `feed_amount`, `water_intake`, `notes`

**Validation rules:**

1. `cow` must exist and `is_alive=True`. Deceased cows cannot have new milk records:
```json
{
  "success": false,
  "error_code": "COW_ALREADY_DECEASED",
  "message": "Cannot add a milk record for a deceased cow."
}
```

2. `collection_date` cannot be in the future:
```json
{
  "success": false,
  "errors": { "collection_date": ["Cannot log milk for a future date."] }
}
```

3. Only one record per cow per day (unique constraint `(cow, collection_date)`). If a record already exists:
```json
{
  "success": false,
  "errors": { "non_field_errors": ["A milk record already exists for this cow on 2026-05-02."] }
}
```

4. If both `morning_yield` and `evening_yield` are provided, `daily_yield` must equal `morning_yield + evening_yield` within 0.5L tolerance:
```json
{
  "success": false,
  "errors": { "non_field_errors": ["daily_yield (12.5) does not match morning_yield (6.8) + evening_yield (5.7) = 12.5"] }
}
```

5. All yield values must be >= 0.0:
```json
{
  "success": false,
  "errors": { "daily_yield": ["Yield cannot be negative."] }
}
```

**Success `201`:** Returns created milk record.

---

### GET `/api/v1/milk/{id}/`

**Auth required:** Any authenticated user

---

### PATCH `/api/v1/milk/{id}/`

**Auth required:** Farmer, Cell Leader

**Request** (all optional):
```json
{
  "daily_yield": 13.0,
  "morning_yield": 7.2,
  "evening_yield": 5.8,
  "notes": "Corrected entry — wrong morning yield recorded initially"
}
```

**Re-validates** the `morning + evening = daily` constraint if all three are present.

---

### DELETE `/api/v1/milk/{id}/`

**Auth required:** Admin only

**Success `204`:** No content. Hard delete.

---

### GET `/api/v1/milk/forecast/?cow_id={id}`

**Auth required:** Any authenticated user

**Query parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `cow_id` | integer | ✅ | Cow to forecast for |

**Processing:**
1. Fetch last 15 `MilkProduction` records for this cow, ordered by `collection_date` descending
2. If fewer than 7 records exist, raise `InsufficientMilkDataError`
3. Call `PredictionService.run_milk_forecast(cow)` which calls `ml_client.predict_milk(...)`
4. Return the forecast result

**Error `400`:** `cow_id` not provided.

**Error `422`:**
```json
{
  "success": false,
  "error_code": "INSUFFICIENT_MILK_DATA",
  "message": "LSTM requires at least 7 days of milk records."
}
```

**Success `200`:**
```json
{
  "success": true,
  "data": {
    "cow_id": 42,
    "forecast_days": 7,
    "forecasts": [
      { "day": 1, "predicted_yield_litres": 12.3, "confidence": "high" },
      { "day": 2, "predicted_yield_litres": 12.1, "confidence": "high" },
      { "day": 3, "predicted_yield_litres": 11.9, "confidence": "high" },
      { "day": 4, "predicted_yield_litres": 11.8, "confidence": "high" },
      { "day": 5, "predicted_yield_litres": 11.7, "confidence": "high" },
      { "day": 6, "predicted_yield_litres": 11.6, "confidence": "high" },
      { "day": 7, "predicted_yield_litres": 11.4, "confidence": "high" }
    ],
    "avg_predicted_yield_litres": 11.97,
    "total_predicted_litres": 83.8,
    "data_quality": "sufficient",
    "note": "Forecast based on ≥15 days — high confidence.",
    "model_version": "v1.0.0"
  }
}
```

---

### GET `/api/v1/milk/summary/`

**Auth required:** Any authenticated user

Returns aggregated production stats for the current user's scope.

**Success `200`:**
```json
{
  "success": true,
  "data": {
    "total_records": 4820,
    "avg_daily_yield": 10.74,
    "total_yield": 51765.8
  }
}
```

**Implementation:**

```python
@action(detail=False, methods=["get"])
def summary(self, request):
    from django.db.models import Avg, Sum
    qs = self.get_queryset()
    return Response({
        "total_records":   qs.count(),
        "avg_daily_yield": round(qs.aggregate(avg=Avg("daily_yield"))["avg"] or 0, 2),
        "total_yield":     round(qs.aggregate(total=Sum("daily_yield"))["total"] or 0, 2),
    })
```

---

## Daily Milk Forecast Celery Task

**Task name:** `features.milk.tasks.run_daily_milk_forecasts`

**Schedule:** Daily at 06:00 AM (seeded in `seed_celery_schedules.py`)

**Logic:**
```python
@shared_task(name="features.milk.tasks.run_daily_milk_forecasts")
def run_daily_milk_forecasts():
    from features.cows.models import Cow
    from features.predictions.services import PredictionService
    cows = Cow.objects.filter(is_alive=True).annotate(
        record_count=Count("milk_records")
    ).filter(record_count__gte=7)
    success, failed, skipped = 0, 0, 0
    for cow in cows:
        try:
            PredictionService.run_milk_forecast(cow)
            success += 1
        except InsufficientMilkDataError:
            skipped += 1
        except Exception as e:
            logger.warning(f"Milk forecast failed for cow {cow.id}: {e}")
            failed += 1
    logger.info(f"Milk forecasts: {success} success, {failed} failed, {skipped} skipped.")
    return {"success": success, "failed": failed, "skipped": skipped}
```

---

## Completion Criteria

- [ ] `GET /milk/` returns role-scoped records with date filters
- [ ] `POST /milk/` creates record with all validations passing
- [ ] `POST /milk/` rejects future dates
- [ ] `POST /milk/` rejects duplicate (cow, date) combinations
- [ ] `POST /milk/` validates `morning + evening = daily` within 0.5L
- [ ] `POST /milk/` rejects negative yields
- [ ] `POST /milk/` rejects records for deceased cows
- [ ] `PATCH /milk/{id}/` updates and re-validates
- [ ] `DELETE /milk/{id}/` hard-deletes (Admin only)
- [ ] `GET /milk/forecast/` returns 7-day forecast or `INSUFFICIENT_MILK_DATA`
- [ ] `GET /milk/summary/` returns aggregate stats
- [ ] `run_daily_milk_forecasts` Celery task is defined and seeded
- [ ] `progress-tracker.md` updated
