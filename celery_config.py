from celery import Celery
from celery.schedules import crontab
from vpnBot import celery_tasks  # do not clear

celery_app = Celery(
    "vpnBot", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)

celery_app.conf.update(
    timezone="Europe/Moscow",
    beat_schedule={
        "periodic_task": {
            "task": "vpnBot.celery_tasks.renew_subscription_task",
            'schedule': crontab(hour="23", minute="59")
        },
    },
)
