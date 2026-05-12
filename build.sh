#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements/production.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Seeding districts..."
python scripts/seed_districts.py

echo "Seeding AI models..."
python scripts/seed_ai_models.py

echo "Seeding Celery schedules..."
python scripts/seed_celery_schedules.py

echo "Build completed successfully!"
