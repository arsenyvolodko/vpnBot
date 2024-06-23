import asyncio
import logging

from celery import shared_task

from vpnBot.renew_subscription import main


logger = logging.getLogger(__name__)


@shared_task
def renew_subscription_task():
    asyncio.run(main())
