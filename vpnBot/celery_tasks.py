import asyncio
import logging

from celery import shared_task
from celery.schedules import crontab

from celery_config import celery_app
from vpnBot.payments import fill_up_balance
from vpnBot.renew_subscription import main

logger = logging.getLogger(__name__)


celery_app.conf.update(
    timezone="Europe/Moscow",
    beat_schedule={
        "periodic_task": {
            "task": "vpnBot.celery_tasks.renew_subscription_task",
            "schedule": crontab(hour="23", minute="55"),
        },
    },
)


@celery_app.task
def renew_subscription_task():
    asyncio.run(main())


@shared_task
def process_payment(payment):
    asyncio.run(fill_up_balance(payment))
