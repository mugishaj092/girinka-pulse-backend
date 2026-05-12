#!/usr/bin/env python
"""
Seeds Celery Beat periodic tasks into the database.
Run once after migrate: python scripts/seed_celery_schedules.py
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "girinka.settings.development")
django.setup()

from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

SCHEDULES = [
    # (minute, hour, day_of_week, day_of_month, task_name, task_path)
    ("0",  "5",  "*", "*", "fetch-daily-weather",          "features.weather.tasks.fetch_daily_weather"),
    ("0",  "6",  "*", "*", "run-daily-milk-forecasts",     "features.milk.tasks.run_daily_milk_forecasts"),
    ("30", "6",  "*", "*", "run-daily-risk-assessment",    "features.predictions.tasks.run_daily_risk_assessment"),
    ("0",  "8",  "1", "*", "weekly-district-reports",      "features.reports.tasks.send_weekly_district_reports"),
    ("0",  "9",  "1", "*", "weekly-national-report",       "features.reports.tasks.send_weekly_national_report"),
    ("0",  "2",  "*", "1", "monthly-model-retrain",        "features.predictions.tasks.monthly_model_retrain"),
    ("0",  "0",  "*", "*", "cleanup-expired-tokens",       "features.auth.tasks.cleanup_expired_tokens"),
    ("0",  "3",  "0", "*", "archive-old-predictions",      "features.predictions.tasks.archive_old_predictions"),
    ("0",  "*/6","*", "*", "escalate-unresolved-alerts",   "features.alerts.tasks.escalate_unresolved_alerts"),
]

for minute, hour, dow, dom, name, task in SCHEDULES:
    cron, _ = CrontabSchedule.objects.get_or_create(
        minute=minute, hour=hour, day_of_week=dow,
        day_of_month=dom, month_of_year="*"
    )
    PeriodicTask.objects.update_or_create(
        name=name,
        defaults={"task": task, "crontab": cron, "enabled": True, "args": json.dumps([])}
    )
    print(f"  ✅ {name}")

print(f"\nSeeded {len(SCHEDULES)} periodic tasks.")
