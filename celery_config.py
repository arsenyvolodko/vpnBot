import logging

from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)


celery_app = Celery(
    "vpnBot",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_app.conf.update(
    timezone="Europe/Moscow",
    enable_utc=True,
    beat_schedule={
        "periodic_task": {
            "task": "vpnBot.celery_tasks.renew_subscription_task",
            "schedule": crontab(hour="23", minute="55"),
        },
    },
)


celery_app.autodiscover_tasks(["vpnBot.celery_tasks"])
