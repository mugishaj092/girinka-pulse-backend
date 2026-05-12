Read `progress-tracker.md`, `architecture-context.md`, `api-context.md`, and `code-standards.md` before starting.

# 06 — Cows

Verify and complete the Cows module. Cows are the core entity of the entire system. Every health record, milk entry, alert, prediction, and pass-on transfer is linked to a cow.

Requires: spec `05-beneficiaries` complete (beneficiaries exist to own cows).

---

## Endpoints

All under `/api/v1/cows/`.

---

### GET `/api/v1/cows/`

**Auth required:** Any authenticated user (data scoped by role)

**Data scoping:**
- `FARMER` → only cows owned by their linked beneficiary
- `CELL_LEADER` / `VETERINARIAN` / `DISTRICT_LEADER` → all cows in their district
- `ADMIN` → all cows nationally

**Query parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `breed` | string | Exact match: `FRIESIAN`, `JERSEY`, `ANKOLE`, `ANKOLE_CROSS`, `FRIESIAN_CROSS`, `JERSEY_CROSS`, `OTHER` |
| `health_status` | string | Exact match: `HEALTHY`, `AT_RISK`, `HIGH_RISK`, `UNDER_TREATMENT`, `CRITICAL`, `EMERGENCY`, `DECEASED`, `FLAGGED_FOR_REVIEW` |
| `is_alive` | boolean | `true` or `false` |
| `district` | integer | District ID |
| `beneficiary` | integer | Beneficiary ID |
| `risk_min` | float | Minimum `mortality_risk_score` |
| `risk_max` | float | Maximum `mortality_risk_score` |
| `search` | string | Match on `tag_number` or `beneficiary__full_name` |
| `ordering` | string | Field to sort: `created_at`, `-created_at`, `mortality_risk_score`, `-mortality_risk_score` |
| `page` | integer | Page number |

**Success `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 42,
      "tag_number": "RW-GAS-2026-001",
      "breed": "FRIESIAN_CROSS",
      "dob": "2022-03-15",
      "age_months": 50,
      "health_status": "HEALTHY",
      "mortality_risk_score": 0.12,
      "origin_type": "DIRECT_PROGRAM",
      "is_alive": true,
      "death_date": null,
      "lactation_number": 2,
      "days_in_milk": 95,
      "beneficiary": 12,
      "beneficiary_name": "UWIMANA Claudine",
      "district": 3,
      "district_name": "Gasabo",
      "created_at": "2026-01-20T09:00:00+02:00"
    }
  ],
  "meta": { "count": 1240, "next": "...", "previous": null }
}
```

---

### POST `/api/v1/cows/`

**Auth required:** Cell Leader, Admin

**Request:**
```json
{
  "tag_number": "RW-GAS-2026-001",
  "breed": "FRIESIAN_CROSS",
  "dob": "2022-03-15",
  "beneficiary": 12,
  "district": 3,
  "origin_type": "DIRECT_PROGRAM"
}
```

**Required fields:** `tag_number`, `breed`, `beneficiary`, `district`

**Optional fields:** `dob`, `origin_type` (defaults to `DIRECT_PROGRAM`)

**Validation:**
- `tag_number` must be unique. If taken:
```json
{
  "success": false,
  "error_code": "DUPLICATE_TAG_NUMBER",
  "message": "This cow tag number already exists in the system."
}
```

**Success `201`:** Returns created cow object.

---

### GET `/api/v1/cows/{id}/`

**Auth required:** Any authenticated user

**Success `200`:** Returns full cow profile.

---

### PATCH `/api/v1/cows/{id}/`

**Auth required:** Cell Leader, Veterinarian, Admin

**Request** (all optional):
```json
{
  "breed": "FRIESIAN",
  "lactation_number": 3,
  "days_in_milk": 45
}
```

**Immutable after creation:** `tag_number`, `beneficiary`, `district`, `origin_type`

**Error `422` — cow is deceased:**
```json
{
  "success": false,
  "error_code": "COW_ALREADY_DECEASED",
  "message": "Cannot update a deceased cow."
}
```

**Implementation:** Override `perform_update()` in `CowViewSet` to check `is_alive` before saving.

---

### POST `/api/v1/cows/{id}/death/`

**Auth required:** Cell Leader, Veterinarian, Admin

**Request:**
```json
{
  "cause": "Severe respiratory illness — ECF suspected"
}
```

**Required:** `cause`

**What happens:**
- Calls `cow.record_death(cause, request.user)` on the model
- `is_alive = False`
- `health_status = "DECEASED"`
- `death_date = today()`
- `death_cause = cause`
- `death_confirmed_by = request.user`

**Error `422` — already deceased:**
```json
{
  "success": false,
  "error_code": "COW_ALREADY_DECEASED",
  "message": "Cannot update a deceased cow."
}
```

**Success `200`:** Returns updated cow object with `is_alive: false`.

---

### POST `/api/v1/cows/{id}/upload_photo/`

**Auth required:** Cell Leader, Admin

**Content-Type:** `multipart/form-data`

**Request:** Upload image file with key `photo`.

**What happens:**
- Calls `shared.cloudinary_utils.upload_cow_photo(photo_file, cow.tag_number)`
- Returns the Cloudinary public URL
- Does **not** store the URL in the cow's database record (photo URL is returned to the caller to store if needed)

**Success `200`:**
```json
{
  "success": true,
  "data": {
    "photo_url": "https://res.cloudinary.com/dhforyx1s/image/upload/v.../girinka/cows/cow_RW-GAS-2026-001.jpg"
  }
}
```

**Error `400`:** No file uploaded.

**Error `500`:** Cloudinary upload failed.

---

### GET `/api/v1/cows/{id}/health/`

Returns last 20 health records for this cow, ordered by `date_recorded` descending.

**Auth required:** Any authenticated user

---

### GET `/api/v1/cows/{id}/milk/`

Returns last 30 milk production records for this cow, ordered by `collection_date` descending.

**Auth required:** Any authenticated user

---

### GET `/api/v1/cows/{id}/alerts/`

Returns all unresolved alerts for this cow, ordered by `alert_timestamp` descending.

**Auth required:** Any authenticated user

---

### GET `/api/v1/cows/{id}/lineage/`

Returns the lineage record for this cow.

**Auth required:** Any authenticated user

**Error `404`:** If no lineage record exists for this cow.

---

### GET `/api/v1/cows/{id}/predictions/`

Returns last 20 AI prediction logs for this cow, ordered by `predicted_at` descending.

**Auth required:** Cell Leader and above

---

### POST `/api/v1/cows/{id}/predict_risk/`

**Auth required:** Cell Leader and above

Triggers a live CatBoost mortality risk prediction for this cow. Calls `PredictionService.run_mortality_check(cow)` synchronously (not queued — latency is acceptable here).

**Error `422`:** If the cow is deceased.

**Success `200`:** Returns the full prediction result from the ML service:
```json
{
  "success": true,
  "data": {
    "cow_id": 42,
    "mortality_risk_score": 0.7155,
    "risk_level": "HIGH",
    "alert_triggered": true,
    "alert_severity": "URGENT",
    "recommended_action": "🔶 Urgent vet consultation within 24 hours.",
    "model_version": "v1.0.0"
  }
}
```

---

### POST `/api/v1/cows/{id}/predict_milk/`

**Auth required:** Any authenticated user

Triggers a live LSTM milk forecast. Calls `PredictionService.run_milk_forecast(cow)`.

**Error `422`:** `INSUFFICIENT_MILK_DATA` if fewer than 7 records exist.

**Success `200`:** Returns 7-day forecast.

---

### GET `/api/v1/cows/at_risk/`

**Auth required:** Cell Leader, Veterinarian, Admin

Returns all living cows with `health_status` in `['AT_RISK', 'HIGH_RISK', 'CRITICAL', 'EMERGENCY']`, ordered by `mortality_risk_score` descending.

Scoped to the user's district for Cell Leader and Vet.

**Success `200`:** Returns paginated list of cow objects.

---

## Completion Criteria

- [ ] `GET /cows/` returns role-scoped data with all filters working
- [ ] `POST /cows/` creates cow with validation
- [ ] `POST /cows/` returns `DUPLICATE_TAG_NUMBER` for existing tag
- [ ] `PATCH /cows/{id}/` updates allowed fields and rejects deceased cow
- [ ] `POST /cows/{id}/death/` records death correctly
- [ ] `POST /cows/{id}/death/` returns `COW_ALREADY_DECEASED` for dead cow
- [ ] `POST /cows/{id}/upload_photo/` returns Cloudinary URL
- [ ] All sub-resource endpoints (`health`, `milk`, `alerts`, `lineage`, `predictions`) return correct data
- [ ] `POST /cows/{id}/predict_risk/` calls ML service and returns result
- [ ] `POST /cows/{id}/predict_milk/` returns 7-day forecast or `INSUFFICIENT_MILK_DATA`
- [ ] `GET /cows/at_risk/` returns at-risk cows sorted by score
- [ ] `progress-tracker.md` updated
