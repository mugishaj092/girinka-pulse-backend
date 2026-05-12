#!/bin/bash
# Girinka Pulse — First-time setup script
# Run once after cloning the repo.

set -e

echo ""
echo "🐄 Girinka Pulse — Setup"
echo "══════════════════════════════════════════"

# 1. Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements/development.txt

# 2. Copy .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ .env created — fill in your values."
else
  echo "ℹ️  .env already exists."
fi

# 3. Run migrations
echo ""
echo "🗄️  Running migrations..."
python manage.py migrate

# 4. Seed Celery Beat schedules
echo ""
echo "⏰ Seeding Celery Beat schedules..."
python scripts/seed_celery_schedules.py

# 5. Create superuser
echo ""
echo "👤 Create admin user:"
python manage.py createsuperuser

echo ""
echo "══════════════════════════════════════════"
echo "✅ Setup complete!"
echo ""
echo "Start the server:      python manage.py runserver"
echo "Start Celery worker:   celery -A girinka worker -l info"
echo "Start Celery beat:     celery -A girinka beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
echo "API docs:              http://localhost:8000/api/v1/docs/"
echo "Admin panel:           http://localhost:8000/admin/"
echo ""
