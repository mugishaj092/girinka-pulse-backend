# Architecture Context

## Stack

| Layer | Technology | Role |
|-------|-----------|------|
| Framework | Django 5 + Django REST Framework | Main API server, routing, serialization |
| Auth | SimpleJWT | JWT access (1h) + refresh (7d) tokens, token blacklist on logout |
| Database | PostgreSQL 15 | Primary data store + Celery message broker (no Redis) |
| Task Queue | Celery + django-celery-beat | Background jobs and scheduled tasks via DB broker |
| Task Results | django-celery-results | Task results stored in PostgreSQL |
| File Storage | Cloudinary | Cow photos, reports, pass-on certificates |
| Email | Resend SDK | Transactional email — alerts, OTP, reports |
| ML Service | FastAPI (external) | 4 trained AI models served via REST at `/predict/*` |
| API Docs | drf-spectacular | Auto-generated Swagger UI with custom branding |

## System Boundaries

- `features/<module>/models.py` — Django ORM models for this feature's tables.
- `features/<module>/serializers.py` — Input validation and output shaping via DRF serializers.
- `features/<module>/views.py` — ViewSets and APIViews. Auth checks, permission enforcement, response shaping. No long-running logic.
- `features/<module>/tasks.py` — Celery tasks for background and scheduled work for this module.
- `features/<module>/filters.py` — django-filter FilterSet classes for list endpoints.
- `features/<module>/urls.py` — URL routing for the module. Registered in `girinka/urls.py`.
- `features/<module>/signals.py` — Django signals for side effects (audit logging, cache invalidation).
- `features/<module>/admin.py` — Django admin registration.
- `shared/` — Cross-cutting infrastructure: permissions, pagination, exceptions, renderers, middleware, utils, cloudinary helpers.
- `girinka/settings/` — Django settings split into `base.py`, `development.py`, `production.py`.
- `girinka/celery.py` — Celery app definition. No schedule hardcoded here — schedules live in DB via django-celery-beat.
- `scripts/seed_celery_schedules.py` — Seeds periodic tasks into DB on first deploy. Run once after `migrate`.

## Module Registry

| Module | Prefix | Key Responsibility |
|--------|--------|--------------------|
| `auth` | `/api/v1/auth/` | Login, logout, token refresh, OTP password reset |
| `users` | `/api/v1/users/` | User CRUD, role management, audit log |
| `districts` | `/api/v1/districts/` | District registry, GPS, live stats, weather proxy |
| `beneficiaries` | `/api/v1/beneficiaries/` | Farmer enrollment, deregistration, bulk CSV import |
| `cows` | `/api/v1/cows/` | Cow lifecycle, health status, death, photo upload |
| `health` | `/api/v1/health/` | Vet records, treatment logs, visit scheduling |
| `milk` | `/api/v1/milk/` | Daily milk entry, LSTM forecast trigger |
| `alerts` | `/api/v1/alerts/` | AI-generated and manual alerts, escalation, resolution |
| `predictions` | `/api/v1/predictions/` | ML service proxy, prediction logs, model management |
| `passon` | `/api/v1/passon/` | Calf transfer workflow, approval, certificates |
| `lineage` | `/api/v1/lineage/` | Cow family tree and genetic records |
| `reports` | `/api/v1/reports/` | Report generation, Cloudinary storage, email delivery |
| `weather` | `/api/v1/weather/` | District weather readings and 7-day forecast |
| `notifications` | `/api/v1/notifications/` | In-app notification inbox and user preferences |

## Database Tables

19 tables across 14 feature modules:

| Table | Module | Notes |
|-------|--------|-------|
| `users` | users | Custom user model, extends AbstractBaseUser |
| `audit_logs` | users | Every CREATE/UPDATE/DELETE/LOGIN action |
| `otp_codes` | users | 6-digit email OTP for password reset, 10-min TTL |
| `districts` | districts | Rwanda districts with GPS lat/lng |
| `beneficiaries` | beneficiaries | Farmers enrolled in Girinka program |
| `cows` | cows | Individual cow records |
| `veterinarians` | health | Vet profiles linked to Users |
| `health_records` | health | Vet visit logs per cow |
| `milk_production` | milk | Daily milk entries per cow |
| `ai_models` | predictions | ML model version registry |
| `prediction_logs` | predictions | Full audit trail of every AI prediction |
| `alerts` | alerts | AI-generated and manual alerts |
| `notification_logs` | alerts | Email delivery records per alert |
| `passon_registry` | passon | Calf transfer records |
| `lineage_records` | lineage | Cow family tree |
| `reports` | reports | Report metadata and Cloudinary URLs |
| `weather_data` | weather | Daily weather readings per district |
| `notifications` | notifications | In-app notification inbox |
| `notification_preferences` | notifications | Per-user notification settings |

## Storage Model

- **PostgreSQL**: all relational metadata — users, cows, beneficiaries, alerts, predictions, relationships, task run records.
- **Cloudinary**: binary artifacts — cow photos (`girinka/cows/`), reports (`girinka/reports/`), pass-on certificates (`girinka/certificates/`).
- Cloudinary URLs are stored in the relevant database records (`file_url`, `certificate_url`, `photo_url`) as the reference to the artifact.
- Do not store file content in the database. Do not store relational metadata in Cloudinary.

## Auth and Role Model

- Every request to a protected endpoint must present a valid `Authorization: Bearer <access_token>` header.
- Five roles exist: `FARMER`, `CELL_LEADER`, `VETERINARIAN`, `DISTRICT_LEADER`, `ADMIN`.
- Data visibility is scoped by role:
  - `FARMER` → own records only
  - `CELL_LEADER` / `VETERINARIAN` → all records in their assigned district
  - `DISTRICT_LEADER` → read-only access across full district
  - `ADMIN` → full national access
- Permission classes live in `shared/permissions.py`. Use them — do not inline permission logic in views.
- OTP password reset uses email only (Resend). No SMS.

## Celery and Scheduled Tasks

All periodic task schedules are stored in the database via `django-celery-beat`. No hardcoded `beat_schedule` in `celery.py`.

Seed schedules once after migrate:
```bash
python scripts/seed_celery_schedules.py
```

| Task | Module | Schedule |
|------|--------|----------|
| `fetch_daily_weather` | weather | Daily 05:00 AM |
| `run_daily_milk_forecasts` | milk | Daily 06:00 AM |
| `run_daily_risk_assessment` | predictions | Daily 06:30 AM |
| `send_weekly_district_reports` | reports | Monday 08:00 AM |
| `send_weekly_national_report` | reports | Monday 09:00 AM |
| `monthly_model_retrain` | predictions | 1st of month 02:00 AM |
| `cleanup_expired_tokens` | auth | Daily midnight |
| `archive_old_predictions` | predictions | Sunday 03:00 AM |
| `escalate_unresolved_alerts` | alerts | Every 6 hours |

## ML Service Integration

The ML FastAPI service runs separately at `ML_SERVICE_URL` (default: `https://girinka-pulse-ml.onrender.com`).

All ML calls go through `features/predictions/ml_client.py` — a thin `httpx` wrapper. No module other than `predictions` should call the ML service directly.

| ML Endpoint | Model | Django trigger |
|-------------|-------|---------------|
| `POST /predict/mortality` | CatBoost M1 | `PredictionService.run_mortality_check(cow)` |
| `POST /predict/milk` | LSTM M2 | `PredictionService.run_milk_forecast(cow)` |
| `POST /predict/disease` | Random Forest M3 | Direct pass-through from `/predictions/disease/` |
| `POST /predict/birth` | Logistic Regression M4 | Direct pass-through from `/predictions/passon/` |
| `GET /health` | — | `/predictions/models/health_check/` |

## Response Format

Every API response is wrapped by `shared/renderers.py`:

```json
{
  "success": true,
  "data": {},
  "message": "OK",
  "errors": null,
  "meta": { "count": 100, "next": "...", "previous": null }
}
```

Error responses include `error_code` for machine-readable classification.

## Invariants

1. Views do not run long-lived AI work or file generation — that belongs in Celery tasks.
2. File content (photos, PDFs, reports) goes to Cloudinary — not the database.
3. Auth and ownership are enforced at every mutation boundary before any business logic runs.
4. Only `features/predictions/ml_client.py` calls the ML service. All other modules call `PredictionService`.
5. Custom exceptions from `shared/exceptions.py` must be raised instead of returning raw HTTP errors from views.
6. Every new periodic task must be seeded via `scripts/seed_celery_schedules.py` — not hardcoded in `celery.py`.
7. The Celery broker is PostgreSQL (`db+postgresql://...`). No Redis dependency exists or should be added.
