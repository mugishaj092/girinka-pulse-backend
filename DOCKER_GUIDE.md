# Docker Setup Guide for Girinka Backend

## Step 1: Start Docker Desktop

1. **Open Docker Desktop**
   - Press `Windows Key`
   - Type "Docker Desktop"
   - Click on "Docker Desktop" application
   - Wait for it to start (this may take 30-60 seconds)

2. **Verify Docker is Running**
   - Look for the Docker whale icon in your system tray (bottom-right corner)
   - The icon should be **steady** (not animated)
   - If it's animated, wait until it stops

3. **Test Docker from Command Line**
   ```bash
   docker ps
   ```
   - If you see a table with columns (even if empty), Docker is ready
   - If you see an error about "cannot connect", Docker Desktop is not fully started yet

---

## Step 2: Build and Start All Services

Once Docker is running, execute these commands:

```bash
# Navigate to the project directory (if not already there)
cd c:\Users\josep\Documents\girinka-backend

# Build and start all containers
docker-compose up --build
```

**What this does:**
- Builds the Django application Docker image
- Pulls PostgreSQL 15 image
- Creates 5 containers:
  - `girinka-db` - PostgreSQL database
  - `girinka-api` - Django REST API server
  - `girinka-worker` - Celery background worker
  - `girinka-beat` - Celery scheduler
  - `girinka-flower` - Task monitoring dashboard

**Expected output:**
- You'll see lots of build logs
- Then container startup logs
- Look for these success messages:
  - `girinka-db | database system is ready to accept connections`
  - `girinka-api | Booting worker with pid: ...`
  - `girinka-worker | celery@... ready`
  - `girinka-beat | beat: Starting...`

**This will take 3-5 minutes on first run** (downloading images + building).

---

## Step 3: Wait for Services to Be Ready

Keep the terminal open. Wait until you see:

```
girinka-api | [INFO] Listening at: http://0.0.0.0:8000
```

This means the API server is ready.

---

## Step 4: Run Verification Checks

**Open a NEW terminal window** (keep the first one running with docker-compose).

### Check 1: Django System Check

```bash
docker exec girinka-api python manage.py check
```

**Expected:** `System check identified no issues (0 silenced).`

---

### Check 2: Database Tables

```bash
docker exec -it girinka-db psql -U postgres -d girinka-pulse-db -c "\dt"
```

**Expected:** List of 19+ tables including:
- users
- audit_logs
- districts
- beneficiaries
- cows
- health_records
- milk_production
- alerts
- etc.

---

### Check 3: Import All Feature Modules

```bash
docker exec girinka-api python manage.py shell -c "
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

**Expected:** `All 14 modules imported successfully.`

---

### Check 4: Shared Infrastructure

```bash
docker exec girinka-api python manage.py shell -c "
from shared.renderers import GirinkaJSONRenderer
from shared.pagination import StandardResultsPagination
from shared.permissions import IsAdmin, IsCellLeaderOrAbove
from shared.exceptions import GirinkaException, InsufficientMilkDataError
from shared.cloudinary_utils import upload_cow_photo
from shared.middleware import RequestLoggingMiddleware
print('All shared modules imported successfully.')
"
```

**Expected:** `All shared modules imported successfully.`

---

### Check 5: Celery Periodic Tasks

```bash
docker exec girinka-api python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
tasks = PeriodicTask.objects.filter(enabled=True).values_list('name', flat=True)
for t in sorted(tasks):
    print(' -', t)
print(f'Total: {len(tasks)} tasks')
"
```

**Expected:** 9 tasks listed:
- archive-old-predictions
- cleanup-expired-tokens
- escalate-unresolved-alerts
- fetch-daily-weather
- monthly-model-retrain
- run-daily-milk-forecasts
- run-daily-risk-assessment
- send-weekly-district-reports
- send-weekly-national-report

**If no tasks appear**, seed them:
```bash
docker exec girinka-api python scripts/seed_celery_schedules.py
```

---

### Check 6: API Routes

```bash
docker exec girinka-api python manage.py show_urls | findstr "api/v1"
```

**Expected:** A number >= 80

---

### Check 7: Swagger Schema Validation

```bash
docker exec girinka-api python manage.py spectacular --validate --fail-on-warn
```

**Expected:** No warnings, no errors

---

### Check 8: Run Tests

```bash
docker exec girinka-api pytest tests/ -v --tb=short
```

**Expected:** All tests pass (35+ tests)

---

### Check 9: Access Swagger UI

Open your browser and go to:

```
http://localhost:8000/api/v1/docs/
```

**Expected:** You should see the Girinka Pulse API documentation with a green header.

---

### Check 10: Test API Health

```bash
curl http://localhost:8000/api/v1/auth/login/
```

**Expected:** JSON response with error about missing credentials (this is correct - it means the endpoint is working)

---

## Step 5: View Container Logs

If anything fails, check the logs:

```bash
# All containers
docker-compose logs

# Specific container
docker-compose logs girinka-api
docker-compose logs girinka-db
docker-compose logs girinka-worker
```

---

## Step 6: Stop All Services

When you're done:

```bash
# Stop all containers (in the terminal running docker-compose)
Press Ctrl+C

# Remove containers
docker-compose down

# Remove containers AND volumes (database data)
docker-compose down -v
```

---

## Troubleshooting

### "Cannot connect to Docker daemon"
- Docker Desktop is not running
- Start Docker Desktop and wait for the whale icon to be steady

### "Port 5432 is already in use"
- You have PostgreSQL running locally
- Stop local PostgreSQL: `net stop postgresql-x64-15` (as admin)
- Or change the port in docker-compose.yml

### "Port 8000 is already in use"
- Another service is using port 8000
- Change the port in docker-compose.yml: `"8001:8000"`

### Containers keep restarting
- Check logs: `docker-compose logs girinka-api`
- Usually means migrations failed or database is not ready

### "No module named 'features'"
- The build didn't copy files correctly
- Run: `docker-compose down && docker-compose up --build`

---

## Quick Reference

```bash
# Start everything
docker-compose up --build

# Start in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Run Django command
docker exec girinka-api python manage.py <command>

# Access Django shell
docker exec -it girinka-api python manage.py shell

# Access PostgreSQL
docker exec -it girinka-db psql -U postgres -d girinka-pulse-db

# Run tests
docker exec girinka-api pytest tests/ -v
```

---

## What's Next?

Once all checks pass, the foundation verification is complete. You can then:

1. Create a superuser:
   ```bash
   docker exec -it girinka-api python manage.py createsuperuser
   ```

2. Access Django admin:
   ```
   http://localhost:8000/admin/
   ```

3. Access Flower (Celery monitoring):
   ```
   http://localhost:5555/
   ```

4. Start building features or integrating with the frontend
