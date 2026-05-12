# Girinka Pulse — Task Board

---

## Task 1 — Foundation Verification

Verify all 10 foundation checks pass: `manage.py check` returns zero issues, all 19 DB tables exist, all 1 4 feature modules import, all 9 Celery tasks are seeded, 80+ routes registered, Swagger validates, and the API server starts.

- [x] `python manage.py check` → zero issues
- [x] All 19 database tables exist
- [x] All 14 feature modules import without error
- [x] All 9 Celery periodic tasks seeded in DB
- [x] 80+ API routes registered
- [x] `spectacular --validate` passes with no warnings
- [x] Swagger UI loads at `/api/v1/docs/`

---

## Task 2 — Database Seed Scripts

Create `scripts/seed_districts.py` (30 Rwanda districts with GPS), `scripts/seed_ai_models.py` (4 ML model versions), and `scripts/create_admin.py`. All scripts must be idempotent. Update `setup.sh` to run them in order.

- [x] `seed_districts.py` creates exactly 30 districts, no duplicates on re-run
- [x] `seed_ai_models.py` creates 4 records, all `is_deployed=True`
- [x] `GET /api/v1/districts/` returns 30 objects
- [x] `GET /api/v1/predictions/models/` returns 4 objects (admin token)
- [x] `setup.sh` runs all seed steps without error

---

## Task 3 — Auth Endpoints

Implement login, logout, token refresh, OTP password reset (request + confirm), password change, and `/me` GET/PATCH. OTP sent via Resend email only. App label must be `auth_feature` to avoid Django's built-in `auth` conflict.

- [x] `POST /auth/login/` returns `access` + `refresh` tokens
- [x] `POST /auth/logout/` blacklists the refresh token
- [x] `POST /auth/token/refresh/` returns new access token
- [x] `POST /auth/password/reset/` sends 6-digit OTP to email
- [x] `POST /auth/password/confirm/` validates OTP and sets new password
- [x] `POST /auth/password/change/` requires old password
- [x] `GET /auth/me/` returns full authenticated user profile
- [x] `PATCH /auth/me/` updates own profile fields

---

## Task 4 — User Management (Admin Only)

Implement full CRUD for user accounts. Soft-delete sets `is_active=False`. Audit log records every mutation. `GET /users/{id}/activity/` returns last 50 audit entries.

- [x] `GET /users/` lists all users, filterable by role and district
- [x] `POST /users/` creates user with assigned role
- [x] `PATCH /users/{id}/` updates user details
- [x] `DELETE /users/{id}/` soft-deactivates (never hard-deletes)
- [x] `GET /users/{id}/activity/` returns last 50 audit log entries
- [x] All actions restricted to Admin role

---

## Task 5 — District Management

Implement district CRUD with `stats` and `weather` actions. Stats endpoint cached 1 hour. Delete blocked if cows or beneficiaries are attached. Public read, Admin-only write.

- [x] `GET /districts/` returns all 30 districts
- [x] `GET /districts/{id}/stats/` returns live cow/beneficiary counts
- [x] `GET /districts/{id}/weather/` proxies latest weather reading
- [x] Delete blocked when cows or beneficiaries exist in district
- [x] Stats response cached for 1 hour

---

## Task 6 — Beneficiary Registration & Lifecycle

Register farmers with Ubudehe category validation (1 or 2 only). Implement deregister (with reason), reregister (Admin only), and bulk CSV import (async Celery task). Deregister blocked if a pass-on transfer is pending.

- [x] `POST /beneficiaries/` validates Ubudehe category 1 or 2
- [x] `POST /beneficiaries/{id}/deregister/` accepts reason enum
- [x] Deregister blocked when `PASSON_PENDING` error raised
- [x] `POST /beneficiaries/{id}/reregister/` Admin only
- [x] `POST /beneficiaries/bulk-import/` returns 202, runs async
- [x] `GET /beneficiaries/{id}/history/` returns program timeline

---

## Task 7 — Cow Lifecycle Management

Full cow CRUD with death recording, photo upload to Cloudinary, and role-scoped list (Farmers see own, Cell Leaders see district, Admins see all). `record_death()` lives on the model and raises `CowAlreadyDeceasedError` if already dead.

- [x] `POST /cows/` registers cow with tag, breed, beneficiary
- [x] `POST /cows/{id}/death/` sets `is_alive=False`, `health_status=DECEASED`
- [x] `POST /cows/{id}/upload_photo/` stores in Cloudinary `girinka/cows/`
- [x] `GET /cows/at_risk/` returns HIGH_RISK/CRITICAL/EMERGENCY cows sorted by risk score
- [x] `CowAlreadyDeceasedError` raised on any action against a dead cow
- [x] Filters work: breed, health_status, is_alive, search

---

## Task 8 — Veterinary Health Records

Implement health record CRUD (Vet and Admin only for write). Include `schedule` action for listing and creating upcoming vet visits. Records store diagnosis, treatment, temperature, weight, and next visit date.

- [x] `POST /health/` creates record with diagnosis and treatment fields
- [x] `GET /health/schedule/` lists upcoming vet visits ordered by date
- [x] `POST /health/schedule/` schedules a new vet visit
- [x] Cell Leaders and Vets see only their district's records
- [x] `GET /cows/{id}/health/` returns last 20 records for a cow

---

## Task 9 — Milk Production Logging & Forecasting

Daily milk entry with morning + evening yield validation (`|daily - (morning + evening)| ≤ 0.5`). LSTM forecast endpoint requires `?cow_id=` and raises `InsufficientMilkDataError` if fewer than 7 records exist. Summary returns aggregate stats scoped to the current user.

- [x] `POST /milk/` validates `daily_yield = morning + evening` within 0.5L
- [x] `GET /milk/forecast/?cow_id=` raises `INSUFFICIENT_MILK_DATA` if < 7 records
- [x] `GET /milk/summary/` returns total records, avg daily yield, total litres
- [x] Farmers see only their own cow records
- [x] `run_daily_milk_forecasts` Celery task runs at 06:00 AM daily

---

## Task 10 — Alert Management & Escalation

AI-generated and manual alerts with resolve, escalate, and bulk resolve. Escalation ladder: `INFO → WARNING → URGENT → CRITICAL`. `escalate_unresolved_alerts` Celery task runs every 6 hours and escalates URGENT alerts older than 24h to CRITICAL.

- [x] `POST /alerts/{id}/resolve/` records resolver, timestamp, and notes
- [x] `POST /alerts/{id}/escalate/` moves severity one level up
- [x] `POST /alerts/bulk_resolve/` accepts `{ "alert_ids": [...] }`
- [x] `GET /alerts/unread_count/` scoped to current user's district
- [x] `escalate_unresolved_alerts` task runs every 6 hours

---

## Task 11 — ML Prediction Endpoints

Proxy endpoints for all 4 ML models (mortality, milk, disease, birth). All HTTP calls go through `ml_client` singleton. `PredictionService` handles feature extraction, alert creation, and email dispatch. `PredictionFailedError` raised on ML service errors.

- [x] `POST /predictions/mortality/` updates `mortality_risk_score` and `health_status`
- [x] `POST /predictions/milk/` triggers low-milk alert if avg < 5 L/day
- [x] `POST /predictions/disease/` returns probabilities for 7 disease classes
- [x] `POST /predictions/disease/` creates DISEASE_OUTBREAK alerts for triggered diseases
- [x] `POST /predictions/disease/` sends email and creates notifications for emergency cases (FMD, Brucellosis)
- [x] `POST /predictions/passon/` returns calving success probability
- [x] `POST /predictions/passon/` creates PASS_ON_DUE alerts for high-risk births (probability < 0.50)
- [x] `POST /predictions/passon/` sends email for critical cases (probability < 0.40)
- [x] All calls go through `ml_client` — no direct `httpx` in views
- [x] `PredictionFailedError` raised and returned as `503` on ML failure
- [x] All prediction responses include `alert_triggered` and `alert_severity` fields

---

## Task 12 — AI Model Administration

Admin endpoints to list model versions, deploy a specific version (deactivates current of same type atomically), view performance metrics, queue a retrain, and health-check the ML service.

- [x] `POST /predictions/models/{id}/deploy/` deactivates current, activates new atomically
- [x] `GET /predictions/models/performance/` returns R², MAE, accuracy per model
- [x] `POST /predictions/models/retrain/` queues retrain on ML service
- [x] `GET /predictions/models/health_check/` confirms all 4 models loaded
- [x] All model admin actions restricted to Admin role

---

## Task 13 — Calf Pass-On Transfer Workflow

Full transfer lifecycle: initiate → approve → complete → certificate. `complete` transfers calf ownership atomically then triggers `generate_passon_certificate` Celery task. Certificate is HTML uploaded to Cloudinary. Both donor and recipient emailed on completion.

- [x] `POST /passon/{id}/approve/` sets `cell_leader_approval=True`, status `APPROVED`
- [x] `POST /passon/{id}/complete/` transfers ownership atomically before triggering task
- [x] `POST /passon/{id}/reject/` sets status `REJECTED` with reason
- [x] `GET /passon/{id}/certificate/` returns 404 if certificate not yet generated
- [x] Donor and recipient both emailed on `complete`

---

## Task 14 — Cow Lineage Records

Read-only lineage viewset with `by_cow` action. Each `LineageRecord` has a OneToOne relation to `Cow` and stores mother reference, generation number, and birth details.

- [x] `GET /lineage/?cow_id=` returns lineage for a specific cow
- [x] `GET /cows/{id}/lineage/` returns mother, generation, birth details
- [x] Lineage records are read-only — no create/update via API
- [x] `LineageRecord` has OneToOne on `Cow`

---

## Task 15 — Report Generation & Distribution

`generate` returns `202 Accepted` immediately; actual generation runs in Celery. Report HTML uploaded to Cloudinary, URL stored in `report.file_url`. Requester emailed when status becomes `READY`. `national` action returns live DB counts with no file generated.

- [x] `POST /reports/generate/` returns 202, triggers Celery task
- [x] Report uploaded to Cloudinary `girinka/reports/` when ready
- [x] Requester emailed via Resend when report is `READY`
- [x] `GET /reports/{id}/download/` returns signed Cloudinary URL
- [x] `GET /reports/national/` returns live national stats (no file)
- [x] `send_weekly_district_reports` and `send_weekly_national_report` tasks run Monday AM

---

## Task 16 — Weather Data Integration

Fetch daily weather from Open-Meteo for all 30 districts at 05:00 AM via Celery. Store `forecast_day` (0 = today, 1–7 = forecast). `forecast` action returns 7-day outlook filterable by district.

- [x] `fetch_daily_weather` task runs daily at 05:00 AM
- [x] Weather fetched for all districts that have GPS coordinates
- [x] `GET /weather/?district_id=` filters by district
- [x] `GET /weather/forecast/` returns 7-day forecast
- [x] `forecast_day=0` is today's reading

---

## Task 17 — In-App Notifications & Preferences

Notification inbox with read/unread state. `mark_all_read` sets `read_at` on all unread notifications for the current user. Preferences control SMS, email, in-app, push toggles and minimum severity threshold.

- [x] `PATCH /notifications/{id}/read/` sets `read_at` timestamp
- [x] `POST /notifications/mark_all_read/` marks all unread at once
- [x] `GET /notifications/settings/` returns current user's preferences
- [x] `PATCH /notifications/settings/` updates preference toggles
- [x] Notifications listed newest first

---

## Task 18 — Celery Scheduled Task Suite

All 9 periodic tasks seeded via `seed_celery_schedules.py` and manageable from Django Admin → Periodic Tasks. Each task logs start, completion, and errors. Each returns a summary dict visible in Flower.

- [x] `fetch_daily_weather` — daily 05:00 AM
- [x] `run_daily_milk_forecasts` — daily 06:00 AM
- [x] `run_daily_risk_assessment` — daily 06:30 AM
- [x] `send_weekly_district_reports` — Monday 08:00 AM
- [x] `send_weekly_national_report` — Monday 09:00 AM
- [x] `monthly_model_retrain` — 1st of month 02:00 AM
- [x] `cleanup_expired_tokens` — daily midnight
- [x] `archive_old_predictions` — Sunday 03:00 AM
- [x] `escalate_unresolved_alerts` — every 6 hours

---

## Task 19 — Test Suite

Integration tests covering auth, cows, beneficiaries, alerts, predictions, and notifications. ML service, Cloudinary, and Resend all mocked. Role permission enforcement tested on every protected endpoint.

- [x] `test_auth.py` — login, logout, `/me` (6+ cases)
- [x] `test_cows.py` — permissions, at_risk, death (6+ cases)
- [x] `test_beneficiaries.py` — registration, deregister, Ubudehe validation (5+ cases)
- [x] `test_alerts.py` — resolve, escalate, bulk_resolve (3+ cases)
- [x] `test_predictions.py` — mortality, milk forecast, ML mocked (7+ cases)
- [x] `test_notifications.py` — Resend mocked, Cloudinary mocked (8+ cases)
- [x] Zero failures, zero errors on `pytest tests/ -v`

---

## Task 20 — Production Deployment Checklist

Configure production settings, Docker Compose with all 5 services, environment hardening, and frontend integration. Seed real district data and register AI model versions on the production server.

- [ ] `production.py` settings: `DEBUG=False`, HTTPS, Sentry configured
- [ ] Docker Compose runs all 5 services: `girinka-db`, `girinka-api`, `girinka-worker`, `girinka-beat`, `girinka-flower`
- [ ] `seed_districts.py` run on production DB — 30 districts present
- [ ] `seed_ai_models.py` run on production DB — 4 models registered
- [ ] `CORS_ALLOWED_ORIGINS` set to Next.js frontend domain
- [ ] Celery worker and Beat running on production server
- [ ] `GET /api/v1/predictions/models/health_check/` returns all 4 models loaded
- [ ] Integration testing with Next.js frontend complete
