# How to Run Girinka Pulse Backend

Complete guide to get the backend running locally on Windows.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.12+** installed
- **PostgreSQL 15+** installed and running
- **Git** installed
- **Code editor** (VS Code recommended)

---

## Quick Start (5 Minutes)

### 1. Clone and Enter Directory

```bash
cd c:\Users\josep\Documents\girinka-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows CMD:**
```bash
venv\Scripts\activate
```

**Windows PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

**Git Bash:**
```bash
source venv/Scripts/activate
```

You should see `(venv)` prefix in your terminal.

### 4. Install Dependencies

```bash
pip install -r requirements\development.txt
```

This installs Django, DRF, Celery, PostgreSQL driver, and all other dependencies.

### 5. Verify `.env` File Exists

Check that `.env` file exists in the root directory:

```bash
type .env
```

It should contain:
```env
SECRET_KEY=girinka-pulse-secret-key-2026
DEBUG=True
DJANGO_SETTINGS_MODULE=girinka.settings.development

DB_NAME=girinka-pulse-db
DB_USER=postgres
DB_PASSWORD=Walmond@123
DB_HOST=localhost
DB_PORT=5432

CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

CLOUDINARY_CLOUD_NAME=dhforyx1s
CLOUDINARY_API_KEY=577771784241754
CLOUDINARY_API_SECRET=nWNOam5NoSZsVq_E4ySFfFZ12fk

RESEND_API_KEY=re_JHLc6JkY_A72P6uHPbXxru9esC9myLZdQ
FROM_EMAIL=Girinka Pulse <no-reply@mugishajoseph.me>

ML_SERVICE_URL=https://girinka-pulse-ml.onrender.com
```

### 6. Create PostgreSQL Database

Open **pgAdmin** or **psql** and run:

```sql
CREATE DATABASE "girinka-pulse-db";
```

**Or via command line:**
```bash
psql -U postgres -c "CREATE DATABASE \"girinka-pulse-db\";"
```

Enter your PostgreSQL password when prompted.

### 7. Run Migrations

```bash
python manage.py migrate
```

You should see output like:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying users.0001_initial... OK
  Applying districts.0001_initial... OK
  ...
  Applying notifications.0002_initial... OK
```

### 8. Seed Reference Data

**Seed 30 Rwanda districts:**
```bash
python scripts\seed_districts.py
```

**Seed 4 AI model versions:**
```bash
python scripts\seed_ai_models.py
```

**Seed Celery periodic tasks:**
```bash
python scripts\seed_celery_schedules.py
```

### 9. Create Admin User

```bash
python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: `admin@girinka.rw`
- Password: (your choice, e.g., `admin123`)
- Password (again): (same)

### 10. Start the Development Server

```bash
python manage.py runserver
```

You should see:
```
Django version 5.0.x, using settings 'girinka.settings.development'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 11. Test the API

Open your browser and visit:

- **Swagger UI:** http://localhost:8000/api/v1/docs/
- **ReDoc:** http://localhost:8000/api/v1/redoc/
- **Django Admin:** http://localhost:8000/admin/

Login to admin with the superuser credentials you created.

---

## Running Background Workers (Celery)

For full functionality (scheduled tasks, async jobs), you need to run Celery workers.

### Option 1: RabbitMQ (Recommended)

**Install RabbitMQ:**

1. Download from: https://www.rabbitmq.com/download.html
2. Install with default settings
3. RabbitMQ will start automatically as a Windows service

**Verify RabbitMQ is running:**
```bash
rabbitmqctl status
```

**Start Celery Worker (Terminal 2):**
```bash
# Activate venv first
venv\Scripts\activate

# Start worker
celery -A girinka worker -l info --pool=solo
```

**Start Celery Beat (Terminal 3):**
```bash
# Activate venv first
venv\Scripts\activate

# Start beat scheduler
celery -A girinka beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Option 2: Without Celery (API Only)

If you don't need background tasks, just run the API server:

```bash
python manage.py runserver
```

Scheduled tasks won't run, but all API endpoints will work.

---

## Full Development Setup (3 Terminals)

**Terminal 1 — Django API:**
```bash
cd c:\Users\josep\Documents\girinka-backend
venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 — Celery Worker:**
```bash
cd c:\Users\josep\Documents\girinka-backend
venv\Scripts\activate
celery -A girinka worker -l info --pool=solo
```

**Terminal 3 — Celery Beat:**
```bash
cd c:\Users\josep\Documents\girinka-backend
venv\Scripts\activate
celery -A girinka beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## Testing the Setup

### 1. Check System Health

```bash
python manage.py check
```

Expected output: `System check identified no issues (0 silenced).`

### 2. Test API Endpoints

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"admin\", \"password\": \"admin123\"}"
```

You should get:
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Get Districts:**
```bash
curl http://localhost:8000/api/v1/districts/
```

Should return 30 Rwanda districts.

### 3. Run Tests

```bash
pytest tests/ -v
```

Expected: All tests pass, zero failures.

---

## Common Issues & Solutions

### Issue 1: `ModuleNotFoundError: No module named 'django'`

**Solution:** Activate virtual environment first
```bash
venv\Scripts\activate
pip install -r requirements\development.txt
```

### Issue 2: `django.db.utils.OperationalError: FATAL: database "girinka-pulse-db" does not exist`

**Solution:** Create the database
```bash
psql -U postgres -c "CREATE DATABASE \"girinka-pulse-db\";"
```

### Issue 3: `psycopg2.OperationalError: FATAL: password authentication failed`

**Solution:** Update `.env` with your PostgreSQL password
```env
DB_PASSWORD=your_actual_postgres_password
```

### Issue 4: `ImportError: cannot import name 'url' from 'django.conf.urls'`

**Solution:** You're using Django 5.x which removed `url()`. The codebase uses `path()` — ensure you're on Django 5.0+
```bash
pip install --upgrade django
```

### Issue 5: Celery worker won't start on Windows

**Solution:** Use `--pool=solo` flag
```bash
celery -A girinka worker -l info --pool=solo
```

### Issue 6: `No module named 'features'`

**Solution:** Run commands from the project root directory
```bash
cd c:\Users\josep\Documents\girinka-backend
python manage.py runserver
```

### Issue 7: Port 8000 already in use

**Solution:** Kill existing process or use different port
```bash
# Use different port
python manage.py runserver 8001

# Or find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `girinka-pulse-secret-key-2026` |
| `DEBUG` | Debug mode | `True` |
| `DJANGO_SETTINGS_MODULE` | Settings module | `girinka.settings.development` |
| `DB_NAME` | PostgreSQL database name | `girinka-pulse-db` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `Walmond@123` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `CELERY_BROKER_URL` | RabbitMQ connection URL | `amqp://guest:guest@localhost:5672//` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | `dhforyx1s` |
| `CLOUDINARY_API_KEY` | Cloudinary API key | `577771784241754` |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | `nWNOam5NoSZsVq_E4ySFfFZ12fk` |
| `RESEND_API_KEY` | Resend API key | `re_JHLc6JkY_A72P6uHPbXxru9esC9myLZdQ` |
| `FROM_EMAIL` | Email sender address | `Girinka Pulse <no-reply@mugishajoseph.me>` |
| `ML_SERVICE_URL` | ML FastAPI service URL | `https://girinka-pulse-ml.onrender.com` |

---

## Project Structure

```
girinka-backend/
├── features/              # 14 feature modules
│   ├── auth/             # Authentication
│   ├── users/            # User management
│   ├── districts/        # Rwanda districts
│   ├── beneficiaries/    # Farmer registration
│   ├── cows/             # Cow lifecycle
│   ├── health/           # Vet records
│   ├── milk/             # Milk production
│   ├── alerts/           # Alert system
│   ├── predictions/      # ML predictions
│   ├── passon/           # Pass-on transfers
│   ├── lineage/          # Cow lineage
│   ├── reports/          # Report generation
│   ├── weather/          # Weather data
│   └── notifications/    # Notifications
├── girinka/              # Django project config
│   ├── settings/         # Settings (base, dev, prod)
│   ├── urls.py           # Root URL router
│   └── celery.py         # Celery config
├── shared/               # Shared utilities
│   ├── permissions.py    # Role permissions
│   ├── exceptions.py     # Custom exceptions
│   ├── renderers.py      # JSON renderer
│   └── cloudinary_utils.py
├── scripts/              # Setup scripts
│   ├── seed_districts.py
│   ├── seed_ai_models.py
│   └── seed_celery_schedules.py
├── tests/                # Test suite
├── docs/                 # Documentation
├── .env                  # Environment variables
├── manage.py             # Django management
└── requirements/         # Dependencies
    ├── base.txt
    ├── development.txt
    └── production.txt
```

---

## Useful Commands

### Django Management

```bash
# Run development server
python manage.py runserver

# Run on different port
python manage.py runserver 8001

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Check for issues
python manage.py check

# Collect static files
python manage.py collectstatic

# Show all URLs
python manage.py show_urls
```

### Database

```bash
# Open database shell
python manage.py dbshell

# Reset database (DANGER: deletes all data)
python manage.py flush

# Dump data to JSON
python manage.py dumpdata > backup.json

# Load data from JSON
python manage.py loaddata backup.json
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ -v --cov=features --cov-report=html

# Run specific test class
pytest tests/test_cows.py::TestCowPermissions -v
```

### Celery

```bash
# Start worker
celery -A girinka worker -l info --pool=solo

# Start beat scheduler
celery -A girinka beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Purge all tasks
celery -A girinka purge

# Inspect active tasks
celery -A girinka inspect active

# Inspect scheduled tasks
celery -A girinka inspect scheduled
```

---

## Next Steps

1. ✅ Backend running at http://localhost:8000
2. ✅ Swagger UI accessible at http://localhost:8000/api/v1/docs/
3. ✅ Admin panel at http://localhost:8000/admin/
4. 📱 Connect your Next.js frontend to `http://localhost:8000/api/v1/`
5. 🧪 Run tests: `pytest tests/ -v`
6. 📊 View Celery tasks in Django Admin → Periodic Tasks

---

## Production Deployment

For production deployment, see:
- `DOCKER_GUIDE.md` — Docker Compose setup
- `README.md` — Full deployment guide
- `girinka/settings/production.py` — Production settings

---

## Support

If you encounter issues:

1. Check `python manage.py check` for configuration errors
2. Check PostgreSQL is running: `psql -U postgres -l`
3. Check RabbitMQ is running: `rabbitmqctl status`
4. Check logs in terminal output
5. Review `.env` file for correct credentials

---

## Quick Reference Card

```bash
# 1. Activate venv
venv\Scripts\activate

# 2. Start API server
python manage.py runserver

# 3. Start Celery worker (optional, new terminal)
celery -A girinka worker -l info --pool=solo

# 4. Start Celery beat (optional, new terminal)
celery -A girinka beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# 5. Run tests
pytest tests/ -v

# 6. Access Swagger UI
# http://localhost:8000/api/v1/docs/
```

---

**You're all set! 🚀**

The backend is now running and ready to accept requests from your frontend.
