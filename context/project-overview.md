# Girinka Pulse — Backend

## Overview

Girinka Pulse is the AI-powered backend for Rwanda's national **Girinka "One Cow Per Family"** poverty reduction program. It manages 500,000+ farmers and 400,000+ cows across all 30 districts of Rwanda.

The backend is a Django REST API that exposes 80+ endpoints across 14 feature modules, integrates with a separate FastAPI ML service for AI predictions, stores files on Cloudinary, and sends transactional email via Resend.

## Goals

1. Manage the full lifecycle of farmers (beneficiaries) enrolled in the Girinka program.
2. Track every cow — registration, health, milk production, and death.
3. Run AI predictions on cow mortality risk, milk yield, disease risk, and birth probability.
4. Generate and deliver alerts when cows are at risk or production drops.
5. Support the pass-on calf transfer workflow with digital certificates.
6. Generate district and national program reports on schedule.
7. Expose a role-based API consumable by the Next.js frontend.

## Core User Flow

1. Admin creates user accounts with assigned roles and districts.
2. Cell Leader registers beneficiary farmers in their district.
3. Cell Leader registers cows and assigns them to beneficiaries.
4. Farmers log daily milk production. Vets log health records.
5. Daily Celery tasks run AI predictions for all active cows.
6. Alerts are created when risk thresholds are exceeded. Emails are sent.
7. Cell Leader manages pass-on transfers when calves are born.
8. Weekly reports are generated and emailed to district and national leaders.
9. Admin monitors ML model performance and triggers retraining.

## Feature Modules

| Module | Status | Description |
|--------|--------|-------------|
| `auth` | ✅ Complete | JWT login/logout, OTP password reset via email |
| `users` | ✅ Complete | User CRUD, roles, audit logging |
| `districts` | ✅ Complete | District registry, live stats, weather proxy |
| `beneficiaries` | ✅ Complete | Farmer enrollment, deregistration, bulk CSV import |
| `cows` | ✅ Complete | Cow lifecycle, health status, death recording, photo upload |
| `health` | ✅ Complete | Vet records, treatment logs, visit scheduling |
| `milk` | ✅ Complete | Daily milk entry, LSTM forecast trigger |
| `alerts` | ✅ Complete | AI-generated alerts, escalation, resolution workflow |
| `predictions` | ✅ Complete | ML service proxy, prediction logs, model management |
| `passon` | ✅ Complete | Calf transfer workflow, certificate generation |
| `lineage` | ✅ Complete | Cow family tree records |
| `reports` | ✅ Complete | Report generation, Cloudinary storage, email delivery |
| `weather` | ✅ Complete | Open-Meteo integration, 7-day forecast |
| `notifications` | ✅ Complete | In-app inbox, user preferences |

## External Services

| Service | Purpose | Config Key |
|---------|---------|-----------|
| PostgreSQL 15 | Database + Celery broker | `DB_*` in `.env` |
| Cloudinary | File storage (photos, reports, certs) | `CLOUDINARY_*` |
| Resend | Transactional email | `RESEND_API_KEY` |
| ML Service (FastAPI) | 4 AI prediction models | `ML_SERVICE_URL` |
| Open-Meteo | Weather data (free, no key needed) | `OPENMETEO_BASE_URL` |

## Scope

### In Scope

- JWT authentication and role-based access control
- Full CRUD for all 14 feature modules
- AI prediction integration with 4 ML models
- Automated daily risk assessments and milk forecasts via Celery
- Email alerts for at-risk cows via Resend
- Pass-on calf transfer workflow with Cloudinary certificate generation
- District and national report generation on schedule
- Swagger UI with custom branding and rich endpoint documentation
- 80+ tests across all modules

### Out of Scope

- Frontend (separate Next.js repo)
- ML model training (separate `girinka-pulse-ml` repo)
- SMS notifications (removed — email only via Resend)
- Redis (removed — PostgreSQL is the Celery broker)
- AWS S3 (removed — Cloudinary is the file store)
- Billing or subscription management
- Mobile applications

## Success Criteria

1. All 14 feature modules have working CRUD endpoints with correct role enforcement.
2. Daily Celery tasks run without errors and produce correct alerts.
3. ML predictions flow through to alerts and emails correctly.
4. Pass-on workflow completes end-to-end with certificate uploaded to Cloudinary.
5. Reports are generated and emailed on schedule.
6. All 80+ tests pass with mocked external services.
7. `python manage.py check` reports zero issues.
