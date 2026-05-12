# Progress Tracker

Update this file after every implementation session. Every entry must reflect the actual state of the code — not the intended state.

---

## Current Phase

**All 14 feature modules — Complete**

The backend is fully implemented and verified with `python manage.py check` returning zero issues.

---

## Current Goal

Ready for integration testing with the frontend or extension of any feature module.

---

## Completed Work

### Foundation

- [x] Django 5 project scaffolded with `girinka/` config directory
- [x] Settings split into `base.py`, `development.py`, `production.py`
- [x] Custom user model (`features/users/models.py`) with 5 roles: `FARMER`, `CELL_LEADER`, `VETERINARIAN`, `DISTRICT_LEADER`, `ADMIN`
- [x] JWT auth via SimpleJWT — access (1h) + refresh (7d), blacklist on logout
- [x] PostgreSQL configured as primary DB and Celery broker (`db+postgresql://`)
- [x] Celery + django-celery-beat — all schedules stored in DB, no hardcoded `beat_schedule`
- [x] `scripts/seed_celery_schedules.py` seeds 9 periodic tasks into DB
- [x] Cloudinary configured as `DEFAULT_FILE_STORAGE`
- [x] Resend SDK configured for all transactional email
- [x] drf-spectacular with custom branded Swagger UI (`templates/swagger-ui.html`)
- [x] Custom `GirinkaJSONRenderer` wraps all responses in standard envelope
- [x] Custom `GirinkaException` hierarchy in `shared/exceptions.py`
- [x] Role permission classes in `shared/permissions.py`
- [x] `shared/cloudinary_utils.py` — upload helpers for photos, reports, certificates
- [x] `features/notifications/utils.py` — Resend email helpers (alert, OTP, report, welcome)
- [x] `shared/middleware.py` — request logging middleware
- [x] `scripts/setup.sh` — first-time setup script

---

### Feature Modules

#### `auth` — ✅ Complete

**Files changed:**
- `features/auth/views.py` — Login, logout, token refresh, OTP reset request, OTP confirm, password change, /me GET/PATCH
- `features/auth/serializers.py` — LoginSerializer, PasswordResetRequestSerializer (email-based), PasswordResetConfirmSerializer, PasswordChangeSerializer
- `features/auth/urls.py` — 8 routes
- `features/auth/tasks.py` — `cleanup_expired_tokens` (daily midnight)
- `features/auth/apps.py` — label `auth_feature` (avoids Django built-in `auth` conflict)

**Key decisions:**
- OTP sent via Resend email only — no SMS
- OTP uses `email` field not `phone_number` on reset request
- App label is `auth_feature` to avoid collision with `django.contrib.auth`

---

#### `users` — ✅ Complete

**Files changed:**
- `features/users/models.py` — `User` (AbstractBaseUser), `AuditLog`, `OTPCode`
- `features/users/serializers.py` — `UserSerializer`, `UserCreateSerializer`, `UserUpdateSerializer`, `AuditLogSerializer`
- `features/users/views.py` — `UserViewSet` (Admin only) + `activity` action
- `features/users/urls.py` — DefaultRouter
- `features/users/apps.py`

**Key decisions:**
- `User.role` uses `UserRole.TextChoices` with 5 values
- Soft-delete: `DELETE` sets `is_active=False`, never hard-deletes
- `AuditLog` records all mutations via `AuditLogMixin` in `shared/mixins.py`
- `OTPCode` TTL is 10 minutes, marked `is_used=True` on consumption

---

#### `districts` — ✅ Complete

**Files changed:**
- `features/districts/models.py` — `District` with lat/lng, `is_remote`, `get_stats()`, `get_latest_weather()`
- `features/districts/serializers.py` — `DistrictSerializer`, `DistrictStatsSerializer`
- `features/districts/views.py` — `DistrictViewSet` + `stats` and `weather` actions
- `features/districts/urls.py`
- `features/districts/apps.py`

**Key decisions:**
- `stats` endpoint cached for 1 hour in local memory cache
- `weather` action proxies to the `weather` module's latest reading for the district
- Delete is allowed only if no related cows or beneficiaries exist

---

#### `beneficiaries` — ✅ Complete

**Files changed:**
- `features/beneficiaries/models.py` — `Beneficiary` with `MLRiskProfile`, `DeregisterReason` enums
- `features/beneficiaries/serializers.py` — `BeneficiarySerializer` (includes `active_cows` count), `BeneficiaryCreateSerializer`, `DeregisterSerializer`
- `features/beneficiaries/views.py` — `BeneficiaryViewSet` + `deregister`, `reregister`, `cows`, `alerts`, `history`, `bulk_import` actions
- `features/beneficiaries/tasks.py` — `process_bulk_import` (async CSV parsing)
- `features/beneficiaries/urls.py`
- `features/beneficiaries/apps.py`

**Key decisions:**
- Ubudehe validation: raises `InvalidUbudehe` if category is not 1 or 2
- `deregister` blocked if `passon_donations.filter(status="PENDING").exists()`
- `bulk_import` sends CSV content as string to Celery task — does not block the request
- `reregister` is Admin-only; clears `deregistered_at` and `deregister_reason`

---

#### `cows` — ✅ Complete

**Files changed:**
- `features/cows/models.py` — `Cow` with `CowBreed`, `HealthStatus`, `OriginType` enums, `record_death()` method, `age_months` property
- `features/cows/serializers.py` — `CowSerializer` (includes `age_months`, `beneficiary_name`, `district_name`), `CowCreateSerializer`, `CowDeathSerializer`
- `features/cows/views.py` — `CowViewSet` with all 14 actions (CRUD + death, upload_photo, health, milk, alerts, lineage, predictions, predict_risk, predict_milk, at_risk)
- `features/cows/filters.py` — `CowFilter` (breed, health_status, is_alive, district, beneficiary, risk_min, risk_max)
- `features/cows/urls.py`
- `features/cows/apps.py`

**Key decisions:**
- `record_death()` is on the model — raises `CowAlreadyDeceasedError` if already dead
- `upload_photo` uses `MultiPartParser` and delegates to `shared/cloudinary_utils.upload_cow_photo()`
- `predict_risk` and `predict_milk` call `PredictionService` — not the ML client directly
- `at_risk` returns cows with status in `AT_RISK`, `HIGH_RISK`, `CRITICAL`, `EMERGENCY`, sorted by `mortality_risk_score` descending

---

#### `health` — ✅ Complete

**Files changed:**
- `features/health/models.py` — `Veterinarian`, `HealthRecord`
- `features/health/serializers.py` — `VeterinarianSerializer`, `HealthRecordSerializer`
- `features/health/views.py` — `HealthRecordViewSet` + `schedule` and `schedule` POST actions
- `features/health/urls.py`
- `features/health/apps.py`

---

#### `milk` — ✅ Complete

**Files changed:**
- `features/milk/models.py` — `MilkProduction` with unique constraint on `(cow, collection_date)`
- `features/milk/serializers.py` — `MilkProductionSerializer` with `daily_yield = morning + evening` validation
- `features/milk/views.py` — `MilkProductionViewSet` + `forecast` and `summary` actions
- `features/milk/tasks.py` — `run_daily_milk_forecasts` (daily 06:00 AM)
- `features/milk/urls.py`
- `features/milk/apps.py`

**Key decisions:**
- `daily_yield` validation: raises serializer error if |daily - (morning + evening)| > 0.5
- `forecast` action requires `?cow_id=` query param, raises `InsufficientMilkDataError` if < 7 records
- `summary` returns aggregate stats for the current user's scope

---

#### `alerts` — ✅ Complete

**Files changed:**
- `features/alerts/models.py` — `Alert` with `AlertType`, `AlertSeverity` enums, `NotificationLog`
- `features/alerts/serializers.py` — `AlertSerializer`
- `features/alerts/views.py` — `AlertViewSet` + `resolve`, `escalate`, `unread_count`, `bulk_resolve` actions
- `features/alerts/tasks.py` — `escalate_unresolved_alerts` (every 6 hours — escalates URGENT alerts older than 24h to CRITICAL)
- `features/alerts/urls.py`
- `features/alerts/apps.py`

**Key decisions:**
- `resolve` records `resolved_by`, `resolved_at`, and optional `resolution_notes`
- `escalate` maps: `INFO` → `WARNING` → `URGENT` → `CRITICAL` (no-op if already CRITICAL)
- `bulk_resolve` accepts `{ "alert_ids": [1, 2, 3] }`, returns count of resolved
- Alerts auto-created by `PredictionService` — not by alert views

---

#### `predictions` — ✅ Complete

**Files changed:**
- `features/predictions/models.py` — `AIModel` with `ModelType` enum, `PredictionLog` with `PredictionType` enum
- `features/predictions/serializers.py` — `AIModelSerializer`, `PredictionLogSerializer`
- `features/predictions/ml_client.py` — `MLClient` singleton (`ml_client`), thin httpx wrapper for all 4 ML endpoints
- `features/predictions/services.py` — `PredictionService` with `run_mortality_check(cow)` and `run_milk_forecast(cow)`, alert creation, email dispatch
- `features/predictions/views.py` — `MortalityPredictionView`, `MilkPredictionView`, `DiseasePredictionView`, `BirthPredictionView`, `PredictionHistoryViewSet`, `AIModelViewSet` (with `deploy`, `performance`, `retrain`, `health_check` actions)
- `features/predictions/tasks.py` — `run_daily_risk_assessment`, `monthly_model_retrain`, `archive_old_predictions`, `trigger_model_retrain`
- `features/predictions/urls.py`
- `features/predictions/apps.py`

**Key decisions:**
- Only `ml_client.py` makes HTTP calls to the ML service — all other modules call `PredictionService`
- `run_mortality_check` pulls features from the DB automatically — caller only passes the `Cow` instance
- `run_milk_forecast` fetches last 15 records from DB, raises `InsufficientMilkDataError` if < 7
- `PredictionService._send_alert_email` sends via Resend — no SMS
- `deploy` action: deactivates all deployed models of same type, activates new one atomically
- Prediction logs are archived after 90 days by `archive_old_predictions`

---

#### `passon` — ✅ Complete

**Files changed:**
- `features/passon/models.py` — `PassOnRegistry` with `PassOnStatus` enum
- `features/passon/serializers.py` — `PassOnSerializer`
- `features/passon/views.py` — `PassOnViewSet` + `approve`, `complete`, `reject`, `certificate` actions
- `features/passon/tasks.py` — `generate_passon_certificate` — generates HTML cert, uploads to Cloudinary, emails donor and recipient
- `features/passon/urls.py`
- `features/passon/apps.py`

**Key decisions:**
- `complete` transfers `calf.beneficiary` ownership in DB atomically before triggering certificate task
- Certificate is HTML (not PDF) uploaded to Cloudinary as raw resource
- Both donor and recipient emailed on `complete`
- `certificate` action returns `404` if `certificate_url` is null (not yet generated)

---

#### `lineage` — ✅ Complete

**Files changed:**
- `features/lineage/models.py` — `LineageRecord` with OneToOne on `Cow`
- `features/lineage/serializers.py` — `LineageSerializer`
- `features/lineage/views.py` — `LineageViewSet` (read-only) + `by_cow` action
- `features/lineage/urls.py`
- `features/lineage/apps.py`

---

#### `reports` — ✅ Complete

**Files changed:**
- `features/reports/models.py` — `Report` with status enum
- `features/reports/serializers.py` — `ReportSerializer`
- `features/reports/views.py` — `ReportViewSet` + `generate`, `download`, `national` actions
- `features/reports/tasks.py` — `generate_report_pdf`, `send_weekly_district_reports`, `send_weekly_national_report`
- `features/reports/urls.py`
- `features/reports/apps.py`

**Key decisions:**
- `generate` returns `202 Accepted` immediately, actual generation runs in Celery
- Report file (HTML) uploaded to Cloudinary, URL stored in `report.file_url`
- Requester emailed via Resend when report status becomes `READY`
- `national` action returns live DB counts — no report file generated

---

#### `weather` — ✅ Complete

**Files changed:**
- `features/weather/models.py` — `WeatherData` with `forecast_day` (0=today, 1–7=forecast)
- `features/weather/serializers.py` — `WeatherDataSerializer`
- `features/weather/views.py` — `WeatherViewSet` + `forecast` action
- `features/weather/tasks.py` — `fetch_daily_weather` (daily 05:00 AM, calls Open-Meteo for all districts with GPS)
- `features/weather/urls.py`
- `features/weather/apps.py`

---

#### `notifications` — ✅ Complete

**Files changed:**
- `features/notifications/models.py` — `NotificationPreference`, `Notification`
- `features/notifications/serializers.py` — `NotificationSerializer`, `NotificationPreferenceSerializer`
- `features/notifications/views.py` — `NotificationViewSet` + `read`, `mark_all_read`, `settings` actions
- `features/notifications/utils.py` — Resend email helpers: `send_email`, `send_alert_email`, `send_password_reset_email`, `send_weekly_report_email`
- `features/notifications/urls.py`
- `features/notifications/apps.py`

---

### Swagger / API Docs — ✅ Complete

**Files changed:**
- `girinka/spectacular_config.py` — Full `SPECTACULAR_SETTINGS` with tags, description, Swagger UI config
- `girinka/settings/base.py` — Imports from `spectacular_config.py`
- `girinka/urls.py` — `template_name="swagger-ui.html"` on swagger view
- `templates/swagger-ui.html` — Custom branded HTML template (green banner, colour-coded methods, monokai theme)
- `features/auth/views.py` — `@extend_schema` on all 8 auth endpoints
- `features/districts/views.py` — `@extend_schema` on all 7 district endpoints
- `features/cows/views.py` — `@extend_schema` on all 14 cow endpoints
- `features/beneficiaries/views.py` — `@extend_schema` on all 10 beneficiary endpoints
- `features/alerts/views.py` — `@extend_schema` on all 7 alert endpoints
- `features/milk/views.py` — `@extend_schema` on all 7 milk endpoints
- `features/predictions/views.py` — `@extend_schema` on all 12 prediction endpoints

---

### Documentation — ✅ Complete

- `README.md` — Full usage guide, stack, setup, endpoints, env vars, docker, tests
- `API_ENDPOINTS.md` — 2,861-line complete endpoint reference with request/response examples
- `PREDICTIONS_ENDPOINTS.md` — Dedicated predictions module reference

---

### Tests — ✅ Complete

**Files:**
- `tests/conftest.py` — Shared fixtures: `api_client`, `district`, `admin_user`, `farmer_user`, `cell_leader_user`, `beneficiary`, `cow`, `auth_admin`, `auth_farmer`, `auth_cl`
- `tests/test_auth.py` — `TestLogin` (3 cases), `TestMe` (3 cases)
- `tests/test_cows.py` — `TestCowPermissions` (5 cases), `TestCowAtRisk` (1 case)
- `tests/test_beneficiaries.py` — `TestBeneficiaryRegistration` (5 cases)
- `tests/test_alerts.py` — `TestAlerts` (3 cases)
- `tests/test_predictions.py` — `TestMortalityPrediction` (5 cases), `TestMilkForecast` (2 cases) — ML mocked
- `tests/test_notifications.py` — `TestResendEmail` (5 cases), `TestCloudinaryUpload` (3 cases) — all mocked

---

### Foundation Verification — ✅ Complete

**Verification Date:** 2026-05-04

**Environment:** Docker (PostgreSQL 15 + RabbitMQ 3.12 + Django 5 + Celery)

**Results:**
- ✅ Check 1: `python manage.py check` — zero issues
- ✅ Check 2: Database tables — 39 tables exist (19 core + Django/Celery tables)
- ✅ Check 3: All 14 feature modules import successfully
- ✅ Check 4: All shared infrastructure imports successfully
- ✅ Check 5: 9 Celery periodic tasks seeded in database
- ✅ Check 6: 180 API routes registered (exceeds 80 minimum)
- ✅ Check 7: Swagger schema validates successfully
- ✅ Check 8: Celery worker running and ready
- ✅ Check 9: Celery beat running and ready
- ✅ Check 10: API server listening at http://localhost:8000

**Architecture Changes:**
- Replaced `db+postgresql://` Celery broker with RabbitMQ (Celery doesn't support PostgreSQL as broker)
- Removed Flower service (not essential for MVP, flower package not in requirements)
- Fixed Swagger schema warnings in beneficiaries and notifications serializers

**All systems operational.**

---

## In Progress

- None.

---

## Next Up

- Integration testing with the Next.js frontend.
- Seed real district data (30 Rwanda districts with GPS coordinates).
- Register real AI model versions in the `ai_models` table after deploying the ML service.
- Set up Celery workers and Beat on the production server.

---

## Open Questions

- None currently.

---

## Architecture Decisions Log

| Decision | Reason | Date |
|----------|--------|------|
| No Redis — RabbitMQ as Celery broker | Celery doesn't support PostgreSQL as broker. RabbitMQ is lightweight and reliable | Session 3 |
| Cloudinary instead of AWS S3 | Easier setup, free tier sufficient, built-in image transformations for cow photos | Session 1 |
| Resend instead of SMTP / Africa's Talking | Simpler API, better deliverability, no SMS needed for this phase | Session 1 |
| OTP via email not SMS | Africa's Talking removed from stack — all user comms go through Resend | Session 1 |
| `django-celery-beat` DB scheduler | Schedules editable via Django admin without redeploying — better for ops | Session 1 |
| `auth` app label is `auth_feature` | Avoids Django's built-in `auth` app label conflict | Session 1 |
| HTML certificates not PDF | WeasyPrint dependency is heavy — HTML uploaded to Cloudinary is sufficient for MVP | Session 1 |
| `@extend_schema` on all views | Required for correct Swagger UI — without it, auto-generated schema is wrong for custom actions | Session 2 |
| Custom `swagger-ui.html` template | drf-spectacular's default template has no branding and no persistent auth | Session 2 |
| Spectacular config in `spectacular_config.py` | Keeps `base.py` clean — large SPECTACULAR_SETTINGS dict belongs in its own file | Session 2 |

---

## Session Notes

### Session 1 — Full backend implementation

- All 14 feature modules implemented from scratch
- 19 database tables, migrations generated
- 9 Celery periodic tasks seeded
- All shared infrastructure written (renderers, exceptions, permissions, cloudinary, email)
- `python manage.py check` → zero issues
- 38 tests written

### Session 2 — Swagger upgrade and documentation

- Added `@extend_schema` decorators to 7 view files (auth, districts, cows, beneficiaries, alerts, milk, predictions)
- Created `girinka/spectacular_config.py` with full tag definitions and Swagger UI config
- Created `templates/swagger-ui.html` with custom branding
- Created `API_ENDPOINTS.md` (2,861 lines)
- Created `PREDICTIONS_ENDPOINTS.md` (1,060 lines)
- Created this context file set

### Session 3 — Foundation verification via Docker

- Identified MSYS2/MinGW Python incompatibility with psycopg2-binary and Pillow
- Switched to Docker-based verification
- Replaced PostgreSQL Celery broker with RabbitMQ (Celery doesn't support PostgreSQL as broker)
- Fixed Swagger schema warnings in beneficiaries and notifications serializers
- Seeded 9 Celery periodic tasks into database
- Verified all 10 foundation checks pass
- All systems operational: API server, Celery worker, Celery beat, PostgreSQL, RabbitMQ
