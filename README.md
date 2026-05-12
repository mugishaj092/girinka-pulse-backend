<div align="center">

# 🐄 Girinka Pulse — Backend API

**Rwanda's "One Cow Per Family" National Program**
AI-powered cow management, health monitoring, and alert system

[![Django](https://img.shields.io/badge/Django-5.0-092E20?style=flat&logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.15-red?style=flat)](https://www.django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat&logo=postgresql)](https://postgresql.org)
[![Cloudinary](https://img.shields.io/badge/Storage-Cloudinary-3448C5?style=flat)](https://cloudinary.com)
[![Resend](https://img.shields.io/badge/Email-Resend-000000?style=flat)](https://resend.com)

**Built by:** UMUTESI Kelia · MUGISHA Joseph · MUGISHA Philippe
**Institution:** University of Rwanda — College of Science & Technology, Year 3

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [All API Endpoints](#-all-api-endpoints)
  - [Authentication](#-authentication)
  - [Users](#-users)
  - [Districts](#-districts)
  - [Beneficiaries](#-beneficiaries)
  - [Cows](#-cows)
  - [Health Records](#-health-records)
  - [Milk Production](#-milk-production)
  - [Alerts](#-alerts)
  - [Predictions (AI)](#-predictions-ai)
  - [Pass-On Registry](#-pass-on-registry)
  - [Lineage](#-lineage)
  - [Reports](#-reports)
  - [Weather](#-weather)
  - [Notifications](#-notifications)
- [Role Permissions](#-role-permissions)
- [Scheduled Tasks](#-scheduled-tasks)
- [File Storage](#-file-storage-cloudinary)
- [Email System](#-email-system-resend)
- [ML Integration](#-ml-integration)
- [Running Tests](#-running-tests)
- [Docker](#-docker)
- [Deployment](#-deployment)

---

## 🌍 Overview

Girinka Pulse is a national-scale Django backend supporting Rwanda's **Girinka "One Cow Per Family"** poverty reduction program. It manages **500,000+ farmers** and **400,000+ cows** across all 30 districts of Rwanda.

### Core capabilities

- ✅ Full cow lifecycle management — registration, health tracking, death recording
- ✅ AI-powered predictions — mortality risk, milk forecasting, disease detection, birth probability
- ✅ Automated email alerts — farmers and cell leaders notified when cows are at risk
- ✅ Pass-on transfer workflow — calf redistribution with certificates uploaded to Cloudinary
- ✅ Role-based access control — 5 user roles with fine-grained permissions
- ✅ Scheduled background tasks — daily risk assessments, milk forecasts, weather data
- ✅ Report generation — district and national reports emailed via Resend

---

## 🛠 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Framework | Django 5 + Django REST Framework | Mature, scalable, batteries included |
| Database | PostgreSQL 15 | Primary DB + Celery message broker (no Redis needed) |
| Task Queue | Celery + django-celery-beat | Background jobs and scheduled tasks |
| File Storage | Cloudinary | Cow photos, reports, pass-on certificates |
| Email | Resend | Transactional emails — alerts, OTPs, reports |
| Auth | SimpleJWT | JWT access + refresh tokens |
| ML Service | FastAPI on Render | 4 trained AI models served as REST API |
| API Docs | drf-spectacular (Swagger UI) | Auto-generated interactive docs |

> **No Redis.** PostgreSQL serves as both the application database and the Celery broker via `db+postgresql://`.

---

## 🗂 Project Structure

```
girinka-backend/
│
├── girinka/                        # Django project config
│   ├── settings/
│   │   ├── base.py                 # Shared settings (DB, Cloudinary, Resend, JWT)
│   │   ├── development.py          # Dev overrides (DEBUG=True, verbose logging)
│   │   └── production.py           # Prod overrides (HTTPS, Sentry)
│   ├── urls.py                     # Root URL router
│   ├── celery.py                   # Celery app + PostgreSQL broker config
│   └── wsgi.py
│
├── features/                       # All feature modules (14 apps)
│   ├── auth/                       # Login, logout, JWT, OTP password reset
│   ├── users/                      # User CRUD, roles, audit logs
│   ├── districts/                  # Rwanda district management
│   ├── beneficiaries/              # Farmer registration and deregistration
│   ├── cows/                       # Cow lifecycle, health status, photos
│   ├── health/                     # Vet records, treatment logs
│   ├── milk/                       # Daily milk entry, LSTM forecast
│   ├── alerts/                     # AI alerts, escalation, resolution
│   ├── predictions/                # ML service integration, prediction logs
│   ├── passon/                     # Calf transfer workflow and certificates
│   ├── lineage/                    # Family tree and genetic records
│   ├── reports/                    # PDF/HTML report generation
│   ├── weather/                    # Open-Meteo weather data per district
│   └── notifications/              # In-app notifications and preferences
│
├── shared/                         # Shared utilities
│   ├── permissions.py              # Role-based permission classes
│   ├── pagination.py               # Standard pagination
│   ├── exceptions.py               # Custom exceptions + error codes
│   ├── renderers.py                # Standard JSON response wrapper
│   ├── middleware.py               # Request logging middleware
│   ├── utils.py                    # OTP, phone formatting, helpers
│   └── cloudinary_utils.py         # Cloudinary upload helpers
│
├── tests/                          # Test suite
│   ├── conftest.py                 # Shared fixtures
│   ├── test_auth.py
│   ├── test_cows.py
│   ├── test_beneficiaries.py
│   ├── test_alerts.py
│   ├── test_predictions.py
│   └── test_notifications.py
│
├── scripts/
│   ├── setup.sh                    # First-time setup script
│   └── seed_celery_schedules.py    # Seeds periodic tasks into DB
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── .env                            # Your configured environment (ready to use)
├── .env.example                    # Template for new deployments
├── Dockerfile
├── docker-compose.yml              # PostgreSQL + API + Celery + Beat + Flower
├── pytest.ini
└── manage.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 15+

### Setup

```bash
# 1. Unzip and enter
unzip girinka-backend.zip && cd girinka-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements/development.txt

# 4. Create PostgreSQL database
psql -U postgres -c 'CREATE DATABASE "girinka-pulse-db";'

# 5. The .env is already configured with your credentials — no changes needed

# 6. Run migrations
python manage.py migrate

# 7. Seed Celery Beat schedules
python scripts/seed_celery_schedules.py

# 8. Create admin user
python manage.py createsuperuser

# 9. Start the server
python manage.py runserver
```

### Running background workers

Open 3 terminals:

```bash
# Terminal 1 — API server
python manage.py runserver

# Terminal 2 — Celery worker
celery -A girinka worker -l info

# Terminal 3 — Celery Beat (scheduled tasks)
celery -A girinka beat -l info \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### URLs

| URL | Description |
|-----|-------------|
| `http://localhost:8000/api/v1/docs/` | Swagger UI (interactive API docs) |
| `http://localhost:8000/api/v1/redoc/` | ReDoc API docs |
| `http://localhost:8000/admin/` | Django admin panel |

---

## 🔐 Environment Variables

Your `.env` is pre-configured. For reference:

```env
# Django
SECRET_KEY=girinka-pulse-secret-key-2026
DEBUG=True
DJANGO_SETTINGS_MODULE=girinka.settings.development

# Database
DB_NAME=girinka-pulse-db
DB_USER=postgres
DB_PASSWORD=Walmond@123
DB_HOST=localhost
DB_PORT=5432

# Celery (uses PostgreSQL — no Redis)
CELERY_BROKER_URL=db+postgresql://postgres:Walmond@123@localhost/girinka-pulse-db

# Cloudinary
CLOUDINARY_CLOUD_NAME=dhforyx1s
CLOUDINARY_API_KEY=577771784241754
CLOUDINARY_API_SECRET=nWNOam5NoSZsVq_E4ySFfFZ12fk

# Resend
RESEND_API_KEY=re_JHLc6JkY_A72P6uHPbXxru9esC9myLZdQ
FROM_EMAIL=Girinka Pulse <no-reply@mugishajoseph.me>

# ML Service
ML_SERVICE_URL=https://girinka-pulse-ml.onrender.com
```

---

## 📡 All API Endpoints

**Base URL:** `http://localhost:8000/api/v1/`

All responses follow this standard format:

```json
{
  "success": true,
  "data": { ... },
  "message": "OK",
  "errors": null,
  "meta": { "count": 100, "next": "...", "previous": null }
}
```

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

### 🔑 Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/login/` | Login with username + password. Returns `access` and `refresh` JWT tokens | ❌ Public |
| `POST` | `/auth/logout/` | Blacklist the refresh token to invalidate the session | ✅ Any |
| `POST` | `/auth/token/refresh/` | Exchange a refresh token for a new access token | ❌ Public |
| `POST` | `/auth/password/reset/` | Request a 6-digit OTP sent to the user's email via Resend | ❌ Public |
| `POST` | `/auth/password/confirm/` | Submit OTP + new password to complete the reset | ❌ Public |
| `POST` | `/auth/password/change/` | Change password for the currently logged-in user (requires old password) | ✅ Any |
| `GET` | `/auth/me/` | Get the full profile of the currently authenticated user | ✅ Any |
| `PATCH` | `/auth/me/` | Update own profile (name, email, phone, district) | ✅ Any |

**Login example:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```

---

### 👥 Users

> Admin only — manage all user accounts in the system.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/users/` | List all users with filtering by role and district | Admin |
| `POST` | `/users/` | Create a new user account with an assigned role | Admin |
| `GET` | `/users/{id}/` | Get full details of a specific user | Admin |
| `PATCH` | `/users/{id}/` | Update user details (name, email, role, district) | Admin |
| `DELETE` | `/users/{id}/` | Soft-deactivate a user account (`is_active=false`) | Admin |
| `GET` | `/users/{id}/activity/` | View the last 50 audit log entries for this user | Admin |

---

### 🗺️ Districts

> Public read. Admin-only write.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/districts/` | List all 30 Rwanda districts with GPS coordinates | ✅ Any |
| `POST` | `/districts/` | Create a new district record | Admin |
| `GET` | `/districts/{id}/` | Get a single district's full details | ✅ Any |
| `PATCH` | `/districts/{id}/` | Update district name, province, GPS coordinates | Admin |
| `DELETE` | `/districts/{id}/` | Delete a district (only if no cows/beneficiaries attached) | Admin |
| `GET` | `/districts/{id}/stats/` | Get live stats: total cows, at-risk count, avg milk yield, total beneficiaries | Cell Leader+ |
| `GET` | `/districts/{id}/weather/` | Get the latest weather reading for this district | ✅ Any |

---

### 🏠 Beneficiaries

> Manages the farmers enrolled in the Girinka program.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/beneficiaries/` | List beneficiaries (filtered by district for Cell Leader, own record for Farmer) | ✅ Any |
| `POST` | `/beneficiaries/` | Register a new farmer (validates Ubudehe category must be 1 or 2) | Cell Leader, Admin |
| `GET` | `/beneficiaries/{id}/` | Full beneficiary profile including program history | ✅ Any |
| `PATCH` | `/beneficiaries/{id}/` | Update beneficiary details (phone, category, etc.) | Cell Leader, Admin |
| `POST` | `/beneficiaries/{id}/deregister/` | Deregister a farmer from the program (requires reason). Blocked if pending pass-on exists | Cell Leader, Admin |
| `POST` | `/beneficiaries/{id}/reregister/` | Reactivate a previously deregistered farmer | Admin only |
| `GET` | `/beneficiaries/{id}/cows/` | List all living cows owned by this beneficiary | ✅ Any |
| `GET` | `/beneficiaries/{id}/alerts/` | List unresolved alerts for this beneficiary's cows | ✅ Any |
| `GET` | `/beneficiaries/{id}/history/` | Full program history and timeline | Cell Leader+ |
| `POST` | `/beneficiaries/bulk-import/` | Upload a CSV file to register many beneficiaries at once (async task) | Admin |

**Deregister body:**
```json
{ "reason": "VOLUNTARY", "notes": "Farmer relocated to Kigali" }
```

Reason options: `NO_LONGER_ELIGIBLE` · `COW_DIED` · `RULE_VIOLATION` · `RELOCATED` · `VOLUNTARY` · `DECEASED` · `LAND_LOSS`

---

### 🐮 Cows

> Core cow lifecycle management.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/cows/` | List cows (Farmers see own cows, Cell Leaders see their district, Admins see all) | ✅ Any |
| `POST` | `/cows/` | Register a new cow with tag number, breed, and assign to a beneficiary | Cell Leader, Admin |
| `GET` | `/cows/{id}/` | Full cow profile including breed, health status, risk score, lactation info | ✅ Any |
| `PATCH` | `/cows/{id}/` | Update cow details (breed, lactation number, days in milk) | Cell Leader, Vet, Admin |
| `POST` | `/cows/{id}/death/` | Record the death of a cow with cause. Sets `is_alive=false` and `health_status=DECEASED` | Cell Leader, Vet, Admin |
| `POST` | `/cows/{id}/upload_photo/` | Upload a cow photo. Stored in Cloudinary at `girinka/cows/` | Cell Leader, Admin |
| `GET` | `/cows/{id}/health/` | Last 20 health/vet records for this cow | ✅ Any |
| `GET` | `/cows/{id}/milk/` | Last 30 daily milk production records | ✅ Any |
| `GET` | `/cows/{id}/alerts/` | All unresolved alerts for this cow | ✅ Any |
| `GET` | `/cows/{id}/lineage/` | Lineage tree showing mother, generation number, birth details | ✅ Any |
| `GET` | `/cows/{id}/predictions/` | Last 20 AI prediction logs for this cow | Cell Leader+ |
| `POST` | `/cows/{id}/predict_risk/` | Trigger a live CatBoost mortality risk prediction for this cow | Cell Leader+ |
| `POST` | `/cows/{id}/predict_milk/` | Trigger a live LSTM 7-day milk forecast for this cow | ✅ Any |
| `GET` | `/cows/at_risk/` | List of all living cows with HIGH, CRITICAL, or EMERGENCY health status, sorted by risk score | Cell Leader, Vet, Admin |
| `GET` | `/cows/?breed=FRIESIAN` | Filter by breed | ✅ Any |
| `GET` | `/cows/?health_status=HIGH_RISK` | Filter by health status | ✅ Any |
| `GET` | `/cows/?is_alive=true` | Filter living cows only | ✅ Any |
| `GET` | `/cows/?search=RW-GAS-001` | Search by tag number or farmer name | ✅ Any |

**Cow health statuses:** `HEALTHY` · `AT_RISK` · `HIGH_RISK` · `UNDER_TREATMENT` · `CRITICAL` · `EMERGENCY` · `DECEASED` · `FLAGGED_FOR_REVIEW`

**Cow breeds:** `FRIESIAN` · `JERSEY` · `ANKOLE` · `ANKOLE_CROSS` · `FRIESIAN_CROSS` · `JERSEY_CROSS` · `OTHER`

**Upload photo example:**
```bash
curl -X POST http://localhost:8000/api/v1/cows/1/upload_photo/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@/path/to/cow_photo.jpg"
```

---

### 🩺 Health Records

> Veterinary visit records, diagnosis, and treatment logs.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/health/` | List health records (filtered to district for Cell Leaders and Vets) | Cell Leader, Vet+ |
| `POST` | `/health/` | Create a new health record — diagnosis, treatment, temperature, weight, next visit date | Vet, Admin |
| `GET` | `/health/{id}/` | Full details of a single health record including AI risk score at visit time | ✅ Any |
| `PATCH` | `/health/{id}/` | Update a health record (add treatment notes, update next visit) | Vet, Admin |
| `GET` | `/health/schedule/` | List all upcoming scheduled vet visits ordered by date | Vet, Cell Leader+ |
| `POST` | `/health/schedule/` | Schedule a new vet visit for a cow | Vet, Admin |

---

### 🥛 Milk Production

> Daily milk entry and LSTM-powered forecasting.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/milk/` | List milk records (Farmers see own cow records, Cell Leaders see district) | ✅ Any |
| `POST` | `/milk/` | Log a daily milk entry (morning yield + evening yield + feed amount + water intake) | Farmer, Cell Leader |
| `GET` | `/milk/{id}/` | Details of a single milk record | ✅ Any |
| `PATCH` | `/milk/{id}/` | Correct a milk entry (e.g. fix a typo in daily yield) | Farmer, Cell Leader |
| `DELETE` | `/milk/{id}/` | Delete a milk entry | Admin |
| `GET` | `/milk/forecast/?cow_id={id}` | Trigger LSTM 7-day milk forecast for a cow (requires 7+ days of records) | ✅ Any |
| `GET` | `/milk/summary/` | Production summary: total records, average daily yield, total litres | ✅ Any |

**Milk entry validation:** `daily_yield` must equal `morning_yield + evening_yield` (within 0.5L tolerance).

**Daily entry body:**
```json
{
  "cow": 1,
  "collection_date": "2026-05-01",
  "morning_yield": 6.8,
  "evening_yield": 5.7,
  "daily_yield": 12.5,
  "feed_amount": 6.0,
  "water_intake": 35.0,
  "notes": "Cow looked healthy today"
}
```

---

### 🚨 Alerts

> AI-generated and manual alerts with full escalation workflow.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/alerts/` | List alerts (Farmers see own, Cell Leaders see district, Admins see all). Filterable by severity and resolved status | ✅ Any |
| `POST` | `/alerts/` | Manually create an alert for a cow | Vet, Admin |
| `GET` | `/alerts/{id}/` | Full alert details including risk score, recommendation, and SMS/email status | ✅ Any |
| `POST` | `/alerts/{id}/resolve/` | Mark an alert as resolved with optional notes. Records resolver and timestamp | Cell Leader, Vet, Admin |
| `POST` | `/alerts/{id}/escalate/` | Escalate alert severity one level up (INFO→WARNING→URGENT→CRITICAL) | Cell Leader+ |
| `GET` | `/alerts/unread_count/` | Count of unresolved alerts for the current user's scope | ✅ Any |
| `POST` | `/alerts/bulk_resolve/` | Resolve multiple alerts at once by passing a list of IDs | Admin |

**Alert types:** `MORTALITY_RISK` · `LOW_MILK` · `DISEASE_OUTBREAK` · `WEATHER_RISK` · `VET_VISIT_DUE` · `PASS_ON_DUE`

**Severity levels:** `INFO` · `WARNING` · `URGENT` · `CRITICAL`

**Resolve body:**
```json
{ "notes": "Vet visited. Cow given treatment. Risk reduced." }
```

**Bulk resolve body:**
```json
{ "alert_ids": [1, 2, 3, 7, 12] }
```

---

### 🤖 Predictions (AI)

> Calls the Girinka ML FastAPI microservice and logs all results.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `POST` | `/predictions/mortality/` | Run CatBoost mortality risk prediction for a cow. Updates `mortality_risk_score` and `health_status`. Creates alert if risk ≥ 0.50 | Cell Leader+ |
| `POST` | `/predictions/milk/` | Run LSTM 7-day milk yield forecast. Triggers low-milk alert if avg < 5 L/day | ✅ Any |
| `POST` | `/predictions/disease/` | Run Random Forest disease risk detection across 7 disease classes (FMD, ECF, Mastitis, etc.) | Vet, Cell Leader+ |
| `POST` | `/predictions/passon/` | Run Logistic Regression birth success probability for a pregnant cow | Cell Leader+ |
| `GET` | `/predictions/history/` | List all prediction logs. Filter by `?cow_id=` | Cell Leader+ |
| `GET` | `/predictions/models/` | List all AI model versions registered in the system | Admin |
| `POST` | `/predictions/models/{id}/deploy/` | Deploy a specific model version (deactivates current) | Admin |
| `GET` | `/predictions/models/performance/` | View metrics for all currently deployed models (R², MAE, accuracy) | Admin |
| `POST` | `/predictions/models/retrain/` | Queue a full model retrain pipeline on the ML service | Admin |
| `GET` | `/predictions/models/health_check/` | Check if the ML FastAPI service is reachable and all 4 models are loaded | Admin |

**Mortality body:**
```json
{ "cow_id": 42 }
```

**Milk body:**
```json
{ "cow_id": 7 }
```

**Disease body:**
```json
{
  "cow_id": 12,
  "breed": "Ankole",
  "age_months": 36,
  "body_temperature_c": 40.5,
  "weight_kg": 280,
  "fever": true,
  "lameness": true,
  "nasal_discharge": true
}
```

---

### 🔄 Pass-On Registry

> Complete calf transfer workflow from initiation to completion and certificate.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/passon/` | List all pass-on transfers (filtered by district for Cell Leaders) | Cell Leader+ |
| `POST` | `/passon/` | Initiate a new calf pass-on transfer between two beneficiaries | Cell Leader, Admin |
| `GET` | `/passon/{id}/` | Full transfer details including donor, recipient, calf, eligibility score, status | ✅ Any |
| `PATCH` | `/passon/{id}/` | Update transfer details (notes, transfer date) | Cell Leader, Admin |
| `POST` | `/passon/{id}/approve/` | Cell Leader approves the transfer. Sets `cell_leader_approval=true` and status to `APPROVED` | Cell Leader, Admin |
| `POST` | `/passon/{id}/complete/` | Mark transfer as complete. Changes calf ownership in DB. Triggers certificate generation + email to both parties | Cell Leader, Admin |
| `POST` | `/passon/{id}/reject/` | Reject a transfer with a reason. Sets status to `REJECTED` | Cell Leader, Admin |
| `GET` | `/passon/{id}/certificate/` | Get the Cloudinary URL for the transfer certificate PDF | ✅ Any |

**Transfer statuses:** `PENDING` → `APPROVED` → `COMPLETED` (or `REJECTED` / `CANCELLED`)

**Initiate transfer body:**
```json
{
  "calf": 15,
  "donor_farmer": 3,
  "recipient_farmer": 8,
  "district": 2,
  "transfer_date": "2026-05-15",
  "notes": "Calf is healthy. Recipient household verified."
}
```

---

### 🧬 Lineage

> Cow family trees, genetic profiles, and breeding records.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/lineage/` | List all lineage records | ✅ Any |
| `GET` | `/lineage/{id}/` | Get a specific lineage record | ✅ Any |
| `GET` | `/lineage/?cow_id={id}` | Get lineage record for a specific cow (shows mother, generation, birth details) | ✅ Any |

---

### 📊 Reports

> Generate, store, and distribute district and national program reports.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/reports/` | List all generated reports (Cell Leaders see district reports only) | Cell Leader+ |
| `POST` | `/reports/generate/` | Queue a new report for generation. Uploaded to Cloudinary + emailed when ready | Cell Leader+ |
| `GET` | `/reports/{id}/` | Report status, data snapshot, and metadata | Cell Leader+ |
| `GET` | `/reports/{id}/download/` | Get the Cloudinary signed URL to download the report file | Cell Leader+ |
| `GET` | `/reports/national/` | Live national statistics: total cows, at-risk count, total beneficiaries, unresolved alerts | District Leader, Admin |

**Report types:** `FARMER_SUMMARY` · `DISTRICT_WEEKLY` · `NATIONAL_MONTHLY` · `VET_PRIORITY` · `PASS_ON_AUDIT` · `AI_PERFORMANCE`

**Generate report body:**
```json
{
  "report_type": "DISTRICT_WEEKLY",
  "report_period": "WEEKLY",
  "district": 3,
  "period_start": "2026-04-25",
  "period_end": "2026-05-02"
}
```

---

### 🌤️ Weather

> Daily climate data fetched from Open-Meteo for all 30 Rwanda districts.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/weather/` | List recent weather readings for all districts | ✅ Any |
| `GET` | `/weather/?district_id={id}` | Filter weather readings for a specific district | ✅ Any |
| `GET` | `/weather/forecast/` | Get 7-day weather forecast (optionally filtered by `?district_id=`) | ✅ Any |

Weather data is fetched automatically every day at **05:00 AM** by the Celery Beat scheduler.

---

### 🔔 Notifications

> In-app notification management and user preferences.

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| `GET` | `/notifications/` | List all notifications for the current user, newest first | ✅ Any |
| `GET` | `/notifications/{id}/` | Get a single notification detail | ✅ Any |
| `PATCH` | `/notifications/{id}/read/` | Mark a single notification as read. Sets `read_at` timestamp | ✅ Any |
| `POST` | `/notifications/mark_all_read/` | Mark all of the current user's unread notifications as read at once | ✅ Any |
| `GET` | `/notifications/settings/` | Get current user's notification preferences (SMS, email, in-app, push, min severity) | ✅ Any |
| `PATCH` | `/notifications/settings/` | Update notification preferences | ✅ Any |

---

## 🛡️ Role Permissions

| Action | Farmer | Cell Leader | Veterinarian | District Leader | Admin |
|--------|:------:|:-----------:|:------------:|:---------------:|:-----:|
| View own cows | ✅ | ✅ | ✅ | ✅ | ✅ |
| View all district cows | ❌ | ✅ | ✅ | ✅ | ✅ |
| View all national cows | ❌ | ❌ | ❌ | ✅ | ✅ |
| Register cow | ❌ | ✅ | ❌ | ❌ | ✅ |
| Upload cow photo | ❌ | ✅ | ❌ | ❌ | ✅ |
| Record cow death | ❌ | ✅ | ✅ | ❌ | ✅ |
| Log milk daily | ✅ | ✅ | ❌ | ❌ | ✅ |
| Add health record | ❌ | ❌ | ✅ | ❌ | ✅ |
| Register beneficiary | ❌ | ✅ | ❌ | ❌ | ✅ |
| Deregister beneficiary | ❌ | ✅ | ❌ | ❌ | ✅ |
| Reregister beneficiary | ❌ | ❌ | ❌ | ❌ | ✅ |
| Approve pass-on | ❌ | ✅ | ❌ | ❌ | ✅ |
| Run AI predictions | ❌ | ✅ | ✅ | ✅ | ✅ |
| Resolve alerts | ❌ | ✅ | ✅ | ❌ | ✅ |
| View district reports | ❌ | ✅ | ✅ | ✅ | ✅ |
| View national reports | ❌ | ❌ | ❌ | ✅ | ✅ |
| Deploy ML models | ❌ | ❌ | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ❌ | ❌ | ✅ |
| View audit logs | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## ⏰ Scheduled Tasks

All tasks are managed via Django Admin → **Periodic Tasks** (seeded by `python scripts/seed_celery_schedules.py`).

| Task | Schedule | What it does |
|------|----------|-------------|
| `fetch_daily_weather` | Daily 05:00 AM | Fetches temperature, rainfall, humidity from Open-Meteo for all 30 districts |
| `run_daily_milk_forecasts` | Daily 06:00 AM | Runs LSTM milk forecast for every cow with 7+ days of records |
| `run_daily_risk_assessment` | Daily 06:30 AM | Runs CatBoost mortality risk check on all living cows. Creates alerts and sends emails |
| `send_weekly_district_reports` | Monday 08:00 AM | Generates weekly report for each district and emails it to district leaders |
| `send_weekly_national_report` | Monday 09:00 AM | Generates national summary report and emails to MINAGRI/RAB admins |
| `monthly_model_retrain` | 1st of month 02:00 AM | Triggers full ML model retrain pipeline on the ML service |
| `cleanup_expired_tokens` | Daily midnight | Removes expired JWT tokens from the database |
| `archive_old_predictions` | Sunday 03:00 AM | Deletes prediction logs older than 90 days to keep the table lean |
| `escalate_unresolved_alerts` | Every 6 hours | Escalates any URGENT alert older than 24 hours to CRITICAL |

---

## ☁️ File Storage (Cloudinary)

All files go to **Cloudinary** — no local disk, no S3.

| File type | Cloudinary folder | Access |
|-----------|-----------------|--------|
| Cow photos | `girinka/cows/` | Public URL |
| Reports (HTML) | `girinka/reports/` | Authenticated (signed URL) |
| Pass-on certificates | `girinka/certificates/` | Authenticated (signed URL) |

Cloudinary credentials are already in your `.env`.

---

## 📧 Email System (Resend)

All emails use **Resend** — no SMTP configuration needed.

| Trigger | Template | Recipients |
|---------|----------|-----------|
| Password reset requested | OTP code with 10-min expiry | The requesting user |
| Mortality risk ≥ 0.60 | Formatted alert with cow tag + recommendation | Farmer email |
| Low milk forecast (< 5 L) | Alert with forecast details | Farmer email |
| Pass-on completed | Certificate link + transfer summary | Donor + recipient |
| Weekly district report ready | Summary table + download link | District leaders |
| National report ready | Summary table + download link | Admin / MINAGRI |

From address: `Girinka Pulse <no-reply@mugishajoseph.me>`

---

## 🧠 ML Integration

The backend calls the **Girinka ML FastAPI service** deployed on Render:

```
https://girinka-pulse-ml.onrender.com
```

| ML Endpoint | Model | What it predicts |
|-------------|-------|-----------------|
| `POST /predict/mortality` | CatBoost | Cow death probability (0–1 score) in next 30 days |
| `POST /predict/milk` | LSTM (Bidirectional) | Daily milk yield for the next 7 days |
| `POST /predict/disease` | Random Forest | Probability of 7 disease types (FMD, ECF, Mastitis, etc.) |
| `POST /predict/birth` | Logistic Regression | Probability of successful calving |

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=features --cov-report=html

# Run a specific test file
pytest tests/test_cows.py -v

# Run a specific test class
pytest tests/test_cows.py::TestCowPermissions -v
```

---

## 🐳 Docker

```bash
# Build and start everything
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f django
docker-compose logs -f celery-worker

# Stop everything
docker-compose down
```

**Services started:**

| Container | Port | Description |
|-----------|------|-------------|
| `girinka-db` | 5432 | PostgreSQL 15 (also Celery broker) |
| `girinka-api` | 8000 | Django API + Gunicorn |
| `girinka-worker` | — | Celery worker (4 concurrent tasks) |
| `girinka-beat` | — | Celery Beat scheduler |
| `girinka-flower` | 5555 | Flower task monitoring dashboard |

---

## 🚀 Deployment

### Deploy to Render (Recommended)

This project is fully configured for deployment to [Render](https://render.com).

**Quick Deploy:**

1. Push your code to GitHub
2. Create a Render account
3. Follow the [5-minute deployment guide](./QUICK_DEPLOY.md)

**Full Documentation:**

- **[RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)** — Complete step-by-step guide
- **[QUICK_DEPLOY.md](./QUICK_DEPLOY.md)** — Quick reference for experienced users
- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** — Track your deployment progress
- **[.env.render](./.env.render)** — Environment variables template

**What's Included:**

✅ Automated build script (`build.sh`)
✅ Database seeding (30 districts, 4 AI models)
✅ Celery worker and beat configuration
✅ SSL/HTTPS enforcement
✅ Production-ready settings
✅ Cloudinary file storage
✅ Resend email service
✅ ML service integration

**Cost:** Free tier available, or $28/month for Starter plan (all services)

**Deploy Time:** ~10 minutes for full setup

---

## 🗄️ Database Tables

| Table | Description |
|-------|-------------|
| `users` | All user accounts (5 roles) |
| `audit_logs` | Every create/update/delete action |
| `otp_codes` | Email OTP codes for password reset |
| `districts` | Rwanda's 30 districts with GPS |
| `beneficiaries` | Enrolled farmer households |
| `cows` | All registered cattle |
| `veterinarians` | Vet profiles linked to users |
| `health_records` | Vet visit records per cow |
| `milk_production` | Daily milk entries per cow |
| `ai_models` | ML model versions and metrics |
| `prediction_logs` | Full audit trail of every AI prediction |
| `alerts` | AI-generated and manual alerts |
| `notification_logs` | Email delivery records |
| `passon_registry` | Calf transfer records |
| `lineage_records` | Cow family trees |
| `reports` | Generated report metadata and Cloudinary URLs |
| `weather_data` | Daily weather readings per district |
| `notifications` | In-app notification inbox |
| `notification_preferences` | Per-user notification settings |

---

## 🔢 Custom Error Codes

When an API call fails with a business logic error, the response includes an `error_code`:

| Error Code | Status | Meaning |
|-----------|--------|---------|
| `INSUFFICIENT_MILK_DATA` | 422 | LSTM needs at least 7 days of milk records |
| `COW_ALREADY_DECEASED` | 422 | Cannot update or predict for a deceased cow |
| `BENEFICIARY_INACTIVE` | 422 | Action blocked because beneficiary is deregistered |
| `PASSON_PENDING` | 422 | Cannot deregister while a pass-on transfer is pending |
| `DUPLICATE_TAG_NUMBER` | 409 | This cow tag number already exists in the system |
| `DUPLICATE_NATIONAL_ID` | 409 | This national ID is already registered |
| `INVALID_UBUDEHE` | 400 | Only Ubudehe categories 1 and 2 qualify for Girinka |
| `MODEL_NOT_DEPLOYED` | 503 | No active ML model found for this prediction type |
| `PREDICTION_FAILED` | 503 | The ML service returned an error |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

<div align="center">

**Girinka Pulse** · University of Rwanda · 2026
UMUTESI Kelia · MUGISHA Joseph · MUGISHA Philippe

</div>
