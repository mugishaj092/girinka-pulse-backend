# Girinka Pulse Docker Containers Explained

## Overview

The Girinka Pulse backend runs as **5 separate containers** that work together. Think of them as 5 specialized workers, each doing a specific job.

---

## 🗄️ Container 1: `girinka-db` (PostgreSQL Database)

**What it does:**
- Stores ALL application data permanently
- Acts as the single source of truth for the entire system

**What data it stores:**
- 👥 Users (farmers, vets, cell leaders, admins)
- 🐄 Cows (500,000+ records with health status, breed, location)
- 🏥 Health records (vet visits, diagnoses, treatments)
- 🥛 Milk production (daily entries from farmers)
- 🚨 Alerts (AI-generated and manual alerts)
- 📊 Predictions (ML model outputs, risk scores)
- 📍 Districts (30 Rwanda districts with GPS coordinates)
- 🌤️ Weather data (daily readings per district)
- 📄 Reports (generated PDF/HTML reports)
- 🔄 Pass-on transfers (calf redistribution records)

**Technology:** PostgreSQL 15 (industry-standard relational database)

**Port:** 5432

**Why it's separate:**
- Data persists even if other containers crash
- Can be backed up independently
- Can scale separately if needed

**Real-world analogy:** 
The filing cabinet in an office — everyone reads from it and writes to it, but the cabinet itself just stores information.

---

## 🌐 Container 2: `girinka-api` (Django REST API Server)

**What it does:**
- Handles ALL incoming HTTP requests from the frontend
- Processes business logic (validation, permissions, calculations)
- Reads from and writes to the database
- Returns JSON responses to the frontend

**What requests it handles:**
- `POST /auth/login/` — User login
- `GET /cows/` — List all cows
- `POST /predictions/mortality/` — Run AI mortality prediction
- `POST /milk/` — Log daily milk production
- `GET /alerts/` — Fetch unresolved alerts
- `POST /beneficiaries/` — Register a new farmer
- ... and 180+ other endpoints

**Technology:** Django 5 + Django REST Framework

**Port:** 8000 (exposed to host machine)

**Why it's separate:**
- Can restart without affecting database or background tasks
- Can scale horizontally (run multiple API containers for high traffic)
- Easier to debug and monitor

**Real-world analogy:**
The receptionist at a hospital — takes requests from patients (frontend), checks records (database), and coordinates with specialists (other services).

---

## ⚙️ Container 3: `girinka-worker` (Celery Background Worker)

**What it does:**
- Executes **long-running tasks** asynchronously (in the background)
- Processes tasks from a queue without blocking the API
- Runs tasks triggered by the API or scheduled by Beat

**What tasks it runs:**
- 🤖 **Daily risk assessment** — Runs CatBoost mortality prediction for all 400,000+ cows (takes 30+ minutes)
- 🥛 **Daily milk forecasts** — Runs LSTM forecast for all lactating cows
- 📧 **Send alert emails** — Sends emails via Resend when alerts are created
- 📊 **Generate reports** — Creates district/national reports and uploads to Cloudinary
- 📄 **Pass-on certificates** — Generates HTML certificates and emails to farmers
- 📥 **Bulk CSV import** — Processes large CSV files for beneficiary registration
- 🗑️ **Archive old predictions** — Deletes prediction logs older than 90 days

**Technology:** Celery (distributed task queue)

**Why it's separate:**
- API responds instantly (doesn't wait for slow tasks)
- Tasks can run in parallel (multiple workers can process different tasks simultaneously)
- If a task fails, it doesn't crash the API
- Can retry failed tasks automatically

**Real-world analogy:**
The kitchen staff in a restaurant — the waiter (API) takes your order and immediately gives you a receipt, then the kitchen (worker) prepares your food in the background.

**Example flow:**
1. User clicks "Generate District Report" in frontend
2. Frontend sends `POST /reports/generate/`
3. API responds immediately with `202 Accepted` and task ID
4. Worker picks up the task from queue
5. Worker generates report (takes 2 minutes)
6. Worker uploads to Cloudinary
7. Worker sends email to requester
8. User gets email with download link

---

## ⏰ Container 4: `girinka-beat` (Celery Scheduler)

**What it does:**
- Acts as a **cron job scheduler** for recurring tasks
- Checks the database every minute for scheduled tasks
- Sends tasks to the worker queue at the right time

**What tasks it schedules:**

| Task | Schedule | What it does |
|------|----------|-------------|
| `fetch_daily_weather` | Daily 05:00 AM | Fetches weather from Open-Meteo for all 30 districts |
| `run_daily_milk_forecasts` | Daily 06:00 AM | Runs LSTM milk forecast for every cow with 7+ days of records |
| `run_daily_risk_assessment` | Daily 06:30 AM | Runs CatBoost mortality check on all living cows, creates alerts |
| `send_weekly_district_reports` | Monday 08:00 AM | Generates weekly report for each district, emails to leaders |
| `send_weekly_national_report` | Monday 09:00 AM | Generates national summary, emails to MINAGRI/RAB |
| `monthly_model_retrain` | 1st of month 02:00 AM | Triggers full ML model retrain on the ML service |
| `cleanup_expired_tokens` | Daily midnight | Removes expired JWT tokens from database |
| `archive_old_predictions` | Sunday 03:00 AM | Deletes prediction logs older than 90 days |
| `escalate_unresolved_alerts` | Every 6 hours | Escalates URGENT alerts older than 24h to CRITICAL |

**Technology:** Celery Beat + django-celery-beat (stores schedules in PostgreSQL)

**Why it's separate:**
- Runs 24/7 without human intervention
- Schedules are editable via Django Admin (no code changes needed)
- If Beat crashes, scheduled tasks are missed but API/worker keep running
- Can be restarted without affecting running tasks

**Real-world analogy:**
The alarm clock or calendar app — reminds you to do tasks at specific times, but doesn't do the tasks itself (that's the worker's job).

**Example flow:**
1. Beat checks database at 06:30 AM
2. Finds `run_daily_risk_assessment` task scheduled for 06:30 AM
3. Beat sends task to RabbitMQ queue
4. Worker picks up task and starts processing
5. Worker runs mortality prediction for all 400,000 cows
6. Worker creates alerts and sends emails
7. Task completes, Beat waits for next scheduled task

---

## 📊 Container 5: `girinka-flower` (Task Monitoring Dashboard)

**What it does:**
- Provides a **web UI** to monitor Celery tasks in real-time
- Shows which tasks are running, completed, or failed
- Displays task execution time, success rate, and error logs

**What you can see:**
- ✅ **Active tasks** — Currently running tasks with progress
- 📋 **Task history** — Last 1000 completed tasks
- ❌ **Failed tasks** — Tasks that crashed with error messages
- 📈 **Statistics** — Task throughput, average execution time
- 👷 **Workers** — How many workers are online and their status
- ⏱️ **Task details** — Input parameters, output results, execution time

**Technology:** Flower (Celery monitoring tool)

**Port:** 5555 (access at http://localhost:5555)

**Why it's separate:**
- Optional — system works without it
- Doesn't affect performance of other containers
- Can be disabled in production to save resources
- Useful for debugging and monitoring during development

**Real-world analogy:**
The security camera system in a warehouse — lets you watch what's happening, but doesn't affect the actual work being done.

**Example use cases:**
- Check if daily risk assessment is still running
- See how long report generation took
- Debug why a task failed (view error traceback)
- Monitor worker CPU/memory usage

---

## 🔗 How They Work Together

### Example 1: User Logs In

```
Frontend → girinka-api → girinka-db
   ↓           ↓             ↓
Request    Validate      Check
           password      user table
   ↓           ↓             ↓
Response ← JWT token ← User found
```

**Containers involved:** API + Database

---

### Example 2: Run Mortality Prediction

```
Frontend → girinka-api → ML Service (external)
   ↓           ↓             ↓
Request    Extract       Run CatBoost
           features      model
   ↓           ↓             ↓
           Save to       Return
           girinka-db    risk score
   ↓           ↓
           Create alert
           in girinka-db
   ↓           ↓
           Queue email
           task to
           RabbitMQ
   ↓           ↓
Response ← Risk score
   
   (Later, asynchronously)
   
   girinka-worker picks up email task
        ↓
   Sends email via Resend
        ↓
   Updates alert in girinka-db
```

**Containers involved:** API + Database + Worker

---

### Example 3: Daily Risk Assessment (Scheduled)

```
06:30 AM arrives
   ↓
girinka-beat checks schedule in girinka-db
   ↓
Beat sends task to RabbitMQ queue
   ↓
girinka-worker picks up task
   ↓
Worker fetches all living cows from girinka-db
   ↓
Worker calls ML Service for each cow (400,000 predictions)
   ↓
Worker saves predictions to girinka-db
   ↓
Worker creates alerts in girinka-db for high-risk cows
   ↓
Worker queues email tasks to RabbitMQ
   ↓
Other workers pick up email tasks
   ↓
Emails sent via Resend
   ↓
Task completes (visible in girinka-flower)
```

**Containers involved:** Beat + Worker + Database + Flower (monitoring)

---

## 🚦 Container Dependencies

```
girinka-db (PostgreSQL)
    ↑
    ├── girinka-api (reads/writes data)
    ├── girinka-worker (reads/writes data)
    └── girinka-beat (reads schedules)

RabbitMQ (message broker)
    ↑
    ├── girinka-api (sends tasks)
    ├── girinka-worker (receives tasks)
    └── girinka-beat (sends scheduled tasks)

girinka-flower (monitoring)
    ↑
    └── Watches RabbitMQ and workers
```

---

## 📦 What Happens When You Run `docker-compose up`

1. **girinka-db** starts first (PostgreSQL)
2. **RabbitMQ** starts (message broker)
3. **girinka-api** starts and connects to database
4. **girinka-worker** starts and connects to database + RabbitMQ
5. **girinka-beat** starts and connects to database + RabbitMQ
6. **girinka-flower** starts and connects to RabbitMQ

All containers run simultaneously and communicate over a Docker network.

---

## 🔧 What Happens When You Run `docker-compose down`

1. All 5 containers stop gracefully
2. Containers are removed
3. **Database data is preserved** (stored in Docker volume)
4. Network is removed

Next time you run `docker-compose up`, all your data is still there.

---

## 💾 Data Persistence

**What survives container restarts:**
- ✅ Database data (users, cows, alerts, etc.)
- ✅ Uploaded files (if using volumes)
- ✅ Celery schedules (stored in database)

**What doesn't survive:**
- ❌ Running tasks (will restart)
- ❌ In-memory cache
- ❌ Active WebSocket connections

---

## 🎯 Why This Architecture?

### Benefits:

1. **Scalability** — Can run multiple workers for heavy load
2. **Reliability** — If API crashes, workers keep running
3. **Performance** — Long tasks don't block API responses
4. **Maintainability** — Each container has one job (single responsibility)
5. **Monitoring** — Flower shows exactly what's happening
6. **Deployment** — Can update one container without affecting others

### Real-world comparison:

**Monolithic (bad):**
```
One giant container doing everything
↓
If it crashes, EVERYTHING stops
```

**Microservices (good):**
```
5 specialized containers
↓
If API crashes, workers keep processing tasks
If worker crashes, API keeps serving requests
```

---

## 🚀 Quick Reference

| Container | Purpose | Port | Can it crash? |
|-----------|---------|------|---------------|
| `girinka-db` | Store data | 5432 | ❌ Critical — everything stops |
| `girinka-api` | Handle HTTP requests | 8000 | ⚠️ Frontend stops working |
| `girinka-worker` | Run background tasks | - | ✅ Tasks queue up, retry later |
| `girinka-beat` | Schedule tasks | - | ✅ Scheduled tasks missed until restart |
| `girinka-flower` | Monitor tasks | 5555 | ✅ Optional — no impact |

---

## 📝 Summary

- **girinka-db** = The brain (stores everything)
- **girinka-api** = The receptionist (handles requests)
- **girinka-worker** = The kitchen staff (does heavy work)
- **girinka-beat** = The alarm clock (schedules tasks)
- **girinka-flower** = The security camera (monitors everything)

All 5 work together to make Girinka Pulse a reliable, scalable, and maintainable system for managing 400,000+ cows across Rwanda.
