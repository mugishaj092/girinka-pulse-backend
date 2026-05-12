read `AGENTS`

Read `progress-tracker.md`, `architecture-context.md`, and `code-standards.md` before starting.

# 00 — Foundation Verification

This is the first spec to run. Its only job is to verify that everything marked complete in `progress-tracker.md` actually works end to end. Do not build anything new. Do not skip any check.

If a check fails, fix it before moving to any other spec.

---

## What To Verify

### 1. Django project starts without errors

```bash
python manage.py check
```

Expected output: `System check identified no issues (0 silenced).`

If any errors appear, fix them before continuing.

---

### 2. All migrations are applied and up to date

```bash
python manage.py migrate --check
```

Expected: no pending migrations.

Then confirm all 19 tables exist by running:

```bash
python manage.py dbshell
\dt
```

Expected tables (all must be present):

- `users`
- `audit_logs`
- `otp_codes`
- `districts`
- `beneficiaries`
- `cows`
- `veterinarians`
- `health_records`
- `milk_production`
- `ai_models`
- `prediction_logs`
- `alerts`
- `notification_logs`
- `passon_registry`
- `lineage_records`
- `reports`
- `weather_data`
- `notifications`
- `notification_preferences`

Plus Celery result and beat tables:
- `django_celery_beat_crontabschedule`
- `django_celery_beat_periodictask`
- `django_celery_results_taskresult`

---

### 3. All 14 feature modules are importable

Run:

```bash
python manage.py shell -c "
import features.auth.views
import features.users.views
import features.districts.views
import features.beneficiaries.views
import features.cows.views
import features.health.views
import features.milk.views
import features.alerts.views
import features.predictions.views
import features.passon.views
import features.lineage.views
import features.reports.views
import features.weather.views
import features.notifications.views
print('All 14 modules imported successfully.')
"
```

Expected: `All 14 modules imported successfully.`

---

### 4. All shared infrastructure is importable

```bash
python manage.py shell -c "
from shared.renderers import GirinkaJSONRenderer
from shared.pagination import StandardResultsPagination
from shared.permissions import IsAdmin, IsCellLeaderOrAbove, IsVetOrAbove
from shared.exceptions import (
    GirinkaException, InsufficientMilkDataError, CowAlreadyDeceasedError,
    BeneficiaryInactiveError, PassonPendingError, DuplicateTagNumberError,
    InvalidUbudehe, ModelNotDeployedError, PredictionFailedError
)
from shared.cloudinary_utils import upload_cow_photo, upload_report_pdf, upload_certificate_pdf
from shared.middleware import RequestLoggingMiddleware
from shared.utils import generate_otp, format_phone_rw
print('All shared modules imported successfully.')
"
```

Expected: `All shared modules imported successfully.`

---

### 5. Notification utils are importable

```bash
python manage.py shell -c "
from features.notifications.utils import (
    send_email, send_alert_email,
    send_password_reset_email, send_weekly_report_email
)
print('Notification utils OK.')
"
```

---

### 6. ML client is importable and configured

```bash
python manage.py shell -c "
from features.predictions.ml_client import ml_client
from features.predictions.services import PredictionService
print('ML client OK. Base URL:', ml_client.base)
"
```

Expected: prints the ML service URL from `ML_SERVICE_URL` env var.

---

### 7. Celery periodic tasks are seeded in the database

```bash
python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
tasks = PeriodicTask.objects.filter(enabled=True).values_list('name', flat=True)
for t in sorted(tasks):
    print(' -', t)
print(f'Total: {len(tasks)} tasks')
"
```

Expected — all 9 tasks must be present:

- `archive-old-predictions`
- `cleanup-expired-tokens`
- `escalate-unresolved-alerts`
- `fetch-daily-weather`
- `monthly-model-retrain`
- `run-daily-milk-forecasts`
- `run-daily-risk-assessment`
- `send-weekly-district-reports`
- `send-weekly-national-report`

If any are missing, run: `python scripts/seed_celery_schedules.py`

---

### 8. All URL routes resolve

```bash
python manage.py show_urls 2>/dev/null | grep "api/v1" | wc -l
```

Expected: at least 80 routes listed.

Also verify the Swagger schema generates without errors:

```bash
python manage.py spectacular --validate --fail-on-warn
```

Expected: no warnings, no errors.

---

### 9. The full test suite passes

```bash
pytest tests/ -v --tb=short 2>&1 | tail -20
```

Expected output includes:
- `test_auth.py` — at least 6 tests pass
- `test_cows.py` — at least 6 tests pass
- `test_beneficiaries.py` — at least 5 tests pass
- `test_alerts.py` — at least 3 tests pass
- `test_predictions.py` — at least 7 tests pass
- `test_notifications.py` — at least 8 tests pass
- Final line: `N passed` with zero failures and zero errors

If any test fails, fix the root cause before continuing. Do not mark this spec complete with failing tests.

---

### 10. API server starts and Swagger UI loads

```bash
python manage.py runserver 8000 &
sleep 3
curl -s http://localhost:8000/api/v1/docs/ | grep -c "Girinka Pulse"
```

Expected: a number greater than 0 (confirms the custom branded Swagger UI is served).

Also verify the health check on the root:

```bash
curl -s http://localhost:8000/api/v1/ | python -m json.tool
```

Expected: JSON with `"success": true` (or equivalent from any registered root endpoint).

---

### 11. `.env` has all required keys

Verify the following keys exist in `.env` (values do not need to be real for local dev):

```
SECRET_KEY
DEBUG
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
DATABASE_SSL
CELERY_BROKER_URL
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
RESEND_API_KEY
FROM_EMAIL
ML_SERVICE_URL
CORS_ALLOWED_ORIGINS
```

If any key is missing, add it before continuing.

---

## Completion Criteria

- [ ] `python manage.py check` — zero issues
- [ ] All 19+ database tables exist
- [ ] All 14 feature module views import without error
- [ ] All shared infrastructure imports without error
- [ ] All 9 Celery periodic tasks are in the database
- [ ] At least 80 API routes registered
- [ ] `spectacular --validate` passes with no warnings
- [ ] All tests pass — zero failures
- [ ] Swagger UI loads at `/api/v1/docs/`
- [ ] `.env` has all required keys

Do not proceed to spec 01 until every box above is checked. Update `progress-tracker.md` with the verification results.
