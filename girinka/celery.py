"""
Celery — uses PostgreSQL as broker (no Redis).
Broker URL format: db+postgresql://user:pass@host/dbname
Results stored in DB via django-celery-results.
Schedules stored in DB via django-celery-beat.
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "girinka.settings.development")

app = Celery("girinka")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
