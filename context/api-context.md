# API Context

## Base URL

```
Development:  http://localhost:8000/api/v1/
Production:   https://api.girinka.rw/api/v1/  (when deployed)
```

## Interactive Docs

```
Swagger UI:  http://localhost:8000/api/v1/docs/
ReDoc:       http://localhost:8000/api/v1/redoc/
Raw schema:  http://localhost:8000/api/v1/schema/
```

The Swagger UI uses a custom branded template (`templates/swagger-ui.html`) with Girinka green color scheme, colour-coded HTTP methods, and persistent auth.

## Auth Header

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

Get a token: `POST /api/v1/auth/login/`

## Standard Response Envelope

Every response — success or error — is wrapped by `shared/renderers.py`:

```json
{
  "success": true,
  "data": {},
  "message": "OK",
  "errors": null,
  "meta": { "count": 100, "next": "...", "previous": null }
}
```

For paginated list endpoints, `data` is the array and `meta` contains pagination fields.

## Error Response Shape

```json
{
  "success": false,
  "data": null,
  "message": "Human-readable description",
  "errors": { "field_name": ["error detail"] },
  "error_code": "MACHINE_READABLE_CODE"
}
```

## Error Codes Reference

| Code | HTTP | Raised By |
|------|------|-----------|
| `INSUFFICIENT_MILK_DATA` | 422 | LSTM forecast with < 7 days records |
| `COW_ALREADY_DECEASED` | 422 | Any mutation on a deceased cow |
| `BENEFICIARY_INACTIVE` | 422 | Any mutation on a deregistered beneficiary |
| `PASSON_PENDING` | 422 | Deregister while a transfer is pending |
| `DUPLICATE_TAG_NUMBER` | 409 | Registering a cow with an existing tag |
| `DUPLICATE_NATIONAL_ID` | 409 | Registering a beneficiary with an existing ID |
| `INVALID_UBUDEHE` | 400 | Ubudehe category 3 or 4 submitted |
| `MODEL_NOT_DEPLOYED` | 503 | No active ML model for this prediction type |
| `PREDICTION_FAILED` | 503 | ML service returned an error or is unreachable |
| `INTERNAL_ERROR` | 500 | Unhandled server exception |

---

## 🔑 Auth — `/api/v1/auth/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/login/` | Login, receive access + refresh tokens | Public |
| `POST` | `/auth/logout/` | Blacklist refresh token | Any |
| `POST` | `/auth/token/refresh/` | Exchange refresh for new access token | Public |
| `POST` | `/auth/password/reset/` | Send 6-digit OTP to registered email | Public |
| `POST` | `/auth/password/confirm/` | Confirm OTP + set new password | Public |
| `POST` | `/auth/password/change/` | Change own password (requires old password) | Any |
| `GET` | `/auth/me/` | Get own user profile | Any |
| `PATCH` | `/auth/me/` | Update own profile fields | Any |

**Login request:**
```json
{ "username": "mugisha_joseph", "password": "securepass123" }
```

**Login response `200`:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": { "id": 1, "username": "mugisha_joseph", "role": "CELL_LEADER", "district": 3 }
}
```

**Password reset flow:** `POST /password/reset/` with `{ "email": "..." }` → OTP sent via Resend → `POST /password/confirm/` with `{ "email": "...", "otp_code": "482951", "new_password": "..." }`

---

## 👥 Users — `/api/v1/users/`

Admin only. Full CRUD on user accounts.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/users/` | List all users | Admin |
| `POST` | `/users/` | Create user account | Admin |
| `GET` | `/users/{id}/` | Get user profile | Admin |
| `PATCH` | `/users/{id}/` | Update user | Admin |
| `DELETE` | `/users/{id}/` | Soft-deactivate user | Admin |
| `GET` | `/users/{id}/activity/` | Last 50 audit log entries | Admin |

**Create request:**
```json
{
  "username": "uwimana_claudine",
  "password": "SecurePass@2026",
  "full_name": "UWIMANA Claudine",
  "email": "claudine@girinka.rw",
  "phone_number": "+250788901234",
  "role": "CELL_LEADER",
  "district": 7
}
```

**Role options:** `FARMER` · `CELL_LEADER` · `VETERINARIAN` · `DISTRICT_LEADER` · `ADMIN`

---

## 🗺️ Districts — `/api/v1/districts/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/districts/` | List all 30 districts | Any |
| `POST` | `/districts/` | Create district | Admin |
| `GET` | `/districts/{id}/` | Get district | Any |
| `PATCH` | `/districts/{id}/` | Update district | Admin |
| `DELETE` | `/districts/{id}/` | Delete district | Admin |
| `GET` | `/districts/{id}/stats/` | Live stats: cows, at-risk, avg milk, beneficiaries | Cell Leader+ |
| `GET` | `/districts/{id}/weather/` | Latest weather reading for district | Any |

**Stats response:**
```json
{ "total_cows": 1240, "at_risk_cows": 87, "avg_milk": 11.3, "total_beneficiaries": 980 }
```

---

## 🏠 Beneficiaries — `/api/v1/beneficiaries/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/beneficiaries/` | List (role-scoped) | Any |
| `POST` | `/beneficiaries/` | Register farmer (Ubudehe 1 or 2 only) | Cell Leader+ |
| `GET` | `/beneficiaries/{id}/` | Full profile | Any |
| `PATCH` | `/beneficiaries/{id}/` | Update | Cell Leader+ |
| `POST` | `/beneficiaries/{id}/deregister/` | Deregister with reason | Cell Leader+ |
| `POST` | `/beneficiaries/{id}/reregister/` | Reactivate deregistered farmer | Admin |
| `GET` | `/beneficiaries/{id}/cows/` | Farmer's living cows | Any |
| `GET` | `/beneficiaries/{id}/alerts/` | Farmer's unresolved alerts | Any |
| `GET` | `/beneficiaries/{id}/history/` | Program history | Cell Leader+ |
| `POST` | `/beneficiaries/bulk-import/` | CSV bulk registration (async) | Admin |

**Deregister reason options:** `NO_LONGER_ELIGIBLE` · `COW_DIED` · `RULE_VIOLATION` · `RELOCATED` · `VOLUNTARY` · `DECEASED` · `LAND_LOSS`

**Error `PASSON_PENDING` (422):** Cannot deregister while a pass-on transfer for this farmer is in `PENDING` status.

**Error `INVALID_UBUDEHE` (400):** Only categories 1 and 2 qualify.

---

## 🐮 Cows — `/api/v1/cows/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/cows/` | List (role-scoped, filterable) | Any |
| `POST` | `/cows/` | Register cow | Cell Leader+ |
| `GET` | `/cows/{id}/` | Full profile | Any |
| `PATCH` | `/cows/{id}/` | Update cow | Cell Leader+ |
| `POST` | `/cows/{id}/death/` | Record death (irreversible) | Cell Leader+ |
| `POST` | `/cows/{id}/upload_photo/` | Upload photo → Cloudinary | Cell Leader+ |
| `GET` | `/cows/{id}/health/` | Last 20 health records | Any |
| `GET` | `/cows/{id}/milk/` | Last 30 milk records | Any |
| `GET` | `/cows/{id}/alerts/` | Unresolved alerts | Any |
| `GET` | `/cows/{id}/lineage/` | Lineage tree | Any |
| `GET` | `/cows/{id}/predictions/` | Last 20 prediction logs | Cell Leader+ |
| `POST` | `/cows/{id}/predict_risk/` | Trigger mortality prediction | Cell Leader+ |
| `POST` | `/cows/{id}/predict_milk/` | Trigger milk forecast | Any |
| `GET` | `/cows/at_risk/` | At-risk cows sorted by score | Cell Leader+ |

**Filters:** `breed`, `health_status`, `is_alive`, `district`, `beneficiary`, `risk_min`, `risk_max`

**Search:** `?search=` matches tag number or farmer name

**Breed options:** `FRIESIAN` · `JERSEY` · `ANKOLE` · `ANKOLE_CROSS` · `FRIESIAN_CROSS` · `JERSEY_CROSS` · `OTHER`

**Health status options:** `HEALTHY` · `AT_RISK` · `HIGH_RISK` · `UNDER_TREATMENT` · `CRITICAL` · `EMERGENCY` · `DECEASED` · `FLAGGED_FOR_REVIEW`

**Photo upload:** `multipart/form-data` with key `photo`. Returns `{ "photo_url": "https://res.cloudinary.com/..." }`

---

## 🩺 Health Records — `/api/v1/health/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health/` | List health records (district-scoped) | Cell Leader+ |
| `POST` | `/health/` | Create vet record | Vet+ |
| `GET` | `/health/{id}/` | Get record | Any |
| `PATCH` | `/health/{id}/` | Update record | Vet+ |
| `GET` | `/health/schedule/` | Upcoming vet visits | Vet+ |
| `POST` | `/health/schedule/` | Schedule vet visit | Vet+ |

**Create request:**
```json
{
  "cow": 42,
  "vet": 5,
  "diagnosis": "Mild respiratory infection",
  "treatment_given": "Oxytetracycline 20mg/kg IM",
  "temperature": 39.8,
  "weight": 380.5,
  "next_visit_date": "2026-05-16",
  "date_recorded": "2026-05-02T10:30:00+02:00"
}
```

---

## 🥛 Milk Production — `/api/v1/milk/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/milk/` | List records (role-scoped) | Any |
| `POST` | `/milk/` | Log daily entry | Farmer+ |
| `GET` | `/milk/{id}/` | Get record | Any |
| `PATCH` | `/milk/{id}/` | Correct record | Farmer+ |
| `DELETE` | `/milk/{id}/` | Delete record | Admin |
| `GET` | `/milk/forecast/?cow_id={id}` | Trigger LSTM forecast | Any |
| `GET` | `/milk/summary/` | Aggregate stats for scope | Any |

**Validation:** `daily_yield` must equal `morning_yield + evening_yield` within 0.5L tolerance.

**Forecast requires:** ≥ 7 days of records. Returns `INSUFFICIENT_MILK_DATA` (422) if not met.

---

## 🚨 Alerts — `/api/v1/alerts/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/alerts/` | List (role-scoped, filterable) | Any |
| `POST` | `/alerts/` | Create manual alert | Vet+ |
| `GET` | `/alerts/{id}/` | Get alert | Any |
| `POST` | `/alerts/{id}/resolve/` | Mark resolved | Cell Leader+ |
| `POST` | `/alerts/{id}/escalate/` | Escalate severity one level | Cell Leader+ |
| `GET` | `/alerts/unread_count/` | Count unresolved in scope | Any |
| `POST` | `/alerts/bulk_resolve/` | Resolve multiple by IDs | Cell Leader+ |

**Alert types:** `MORTALITY_RISK` · `LOW_MILK` · `DISEASE_OUTBREAK` · `WEATHER_RISK` · `VET_VISIT_DUE` · `PASS_ON_DUE`

**Severity levels:** `INFO` → `WARNING` → `URGENT` → `CRITICAL`

**Escalation path:** `INFO` → `WARNING` → `URGENT` → `CRITICAL` (no further escalation from CRITICAL)

**Auto-created alerts:**
- `MORTALITY_RISK` when CatBoost score ≥ 0.50
- `LOW_MILK` when LSTM avg forecast < 5 L/day

**Auto-email:** Alert email via Resend when mortality score ≥ 0.60

---

## 🤖 Predictions — `/api/v1/predictions/`

All prediction endpoints call the ML FastAPI service at `ML_SERVICE_URL`. Every result is logged in `PredictionLog`.

| Method | Endpoint | ML Model Called | Auth |
|--------|----------|----------------|------|
| `POST` | `/predictions/mortality/` | `POST /predict/mortality` — CatBoost | Cell Leader+ |
| `POST` | `/predictions/milk/` | `POST /predict/milk` — LSTM | Any |
| `POST` | `/predictions/disease/` | `POST /predict/disease` — Random Forest | Vet+ |
| `POST` | `/predictions/passon/` | `POST /predict/birth` — Logistic Regression | Cell Leader+ |
| `GET` | `/predictions/history/` | — | Cell Leader+ |
| `GET` | `/predictions/history/{id}/` | — | Cell Leader+ |
| `GET` | `/predictions/models/` | — | Admin |
| `GET` | `/predictions/models/{id}/` | — | Admin |
| `POST` | `/predictions/models/{id}/deploy/` | — | Admin |
| `GET` | `/predictions/models/performance/` | — | Admin |
| `POST` | `/predictions/models/retrain/` | `POST /retrain` | Admin |
| `GET` | `/predictions/models/health_check/` | `GET /health` | Admin |

**Mortality request:** `{ "cow_id": 42 }` — all features pulled from DB automatically.

**Mortality risk levels:**

| Score | Level | Email Sent |
|-------|-------|-----------|
| 0.90–1.00 | `EMERGENCY` | ✅ farmer + cell leader + vet |
| 0.80–0.89 | `VERY_HIGH` | ✅ farmer + cell leader |
| 0.60–0.79 | `HIGH` | ✅ farmer |
| 0.50–0.59 | `MEDIUM` | ❌ |
| 0.00–0.49 | `LOW` / `MEDIUM_LOW` | ❌ |

**Disease thresholds:**

| Disease | Threshold | Emergency |
|---------|-----------|-----------|
| `FMD` | 0.60 | ✅ |
| `ECF` | 0.55 | ❌ |
| `Mastitis` | 0.50 | ❌ |
| `Respiratory` | 0.55 | ❌ |
| `Nutritional_Deficiency` | 0.65 | ❌ |
| `Brucellosis` | 0.70 | ✅ |
| `LSD` | 0.60 | ❌ |

**Birth prognosis:**

| Score | Label | Pass-On Eligible |
|-------|-------|-----------------|
| 0.86–1.00 | `Excellent` | ✅ |
| 0.66–0.85 | `Good` | ❌ |
| 0.41–0.65 | `Moderate` | ❌ |
| 0.00–0.40 | `High Risk` | ❌ |

---

## 🔄 Pass-On Registry — `/api/v1/passon/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/passon/` | List transfers (district-scoped) | Cell Leader+ |
| `POST` | `/passon/` | Initiate transfer | Cell Leader+ |
| `GET` | `/passon/{id}/` | Get transfer | Any |
| `PATCH` | `/passon/{id}/` | Update notes/date | Cell Leader+ |
| `POST` | `/passon/{id}/approve/` | Approve transfer | Cell Leader+ |
| `POST` | `/passon/{id}/complete/` | Complete + change ownership | Cell Leader+ |
| `POST` | `/passon/{id}/reject/` | Reject transfer | Cell Leader+ |
| `GET` | `/passon/{id}/certificate/` | Get Cloudinary certificate URL | Any |

**Status flow:** `PENDING` → `APPROVED` → `COMPLETED` (or `REJECTED` / `CANCELLED`)

**On complete:** Calf ownership transferred in DB. Certificate generated and uploaded to Cloudinary. Email sent to donor and recipient via Resend.

---

## 🧬 Lineage — `/api/v1/lineage/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/lineage/` | List lineage records | Any |
| `GET` | `/lineage/{id}/` | Get lineage record | Any |
| `GET` | `/lineage/?cow_id={id}` | Get lineage for specific cow | Any |

---

## 📊 Reports — `/api/v1/reports/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/reports/` | List reports | Cell Leader+ |
| `POST` | `/reports/generate/` | Queue report generation | Cell Leader+ |
| `GET` | `/reports/{id}/` | Get report status + snapshot | Cell Leader+ |
| `GET` | `/reports/{id}/download/` | Get Cloudinary download URL | Cell Leader+ |
| `GET` | `/reports/national/` | Live national stats | District Leader+ |

**Report types:** `FARMER_SUMMARY` · `DISTRICT_WEEKLY` · `NATIONAL_MONTHLY` · `VET_PRIORITY` · `PASS_ON_AUDIT` · `AI_PERFORMANCE`

**Generation is async.** Status progresses: `PENDING` → `GENERATING` → `READY` (or `FAILED`). Report file uploaded to Cloudinary. Requester emailed when ready.

---

## 🌤️ Weather — `/api/v1/weather/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/weather/` | List recent readings | Any |
| `GET` | `/weather/{id}/` | Get single reading | Any |
| `GET` | `/weather/forecast/?district_id={id}` | 7-day forecast | Any |

Data auto-fetched daily at 05:00 AM from Open-Meteo via `fetch_daily_weather` Celery task.

---

## 🔔 Notifications — `/api/v1/notifications/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/notifications/` | List own notifications | Any |
| `GET` | `/notifications/{id}/` | Get notification | Any |
| `PATCH` | `/notifications/{id}/read/` | Mark as read | Any |
| `POST` | `/notifications/mark_all_read/` | Mark all read | Any |
| `GET` | `/notifications/settings/` | Get preferences | Any |
| `PATCH` | `/notifications/settings/` | Update preferences | Any |

**Preferences fields:** `email` (bool), `in_app` (bool), `push` (bool), `min_severity` (string)

---

## Pagination

All list endpoints are paginated. Default page size: 20. Max: 100.

```
?page=2&page_size=50
```

---

## Filtering and Search

List endpoints support:
- `?search=` — full-text search on declared `search_fields`
- `?ordering=field` / `?ordering=-field` — sort ascending/descending
- Field-specific filters declared in `filters.py` for each module
