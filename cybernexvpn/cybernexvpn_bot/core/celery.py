import logging

from celery import Celery

from cybernexvpn.cybernexvpn_bot import config

logger = logging.getLogger(__name__)


app = Celery(
    "cybernexvpn.cybernexvpn_bot",
    broker=config.REDIS_BROKER,
    backend=config.REDIS_BACKEND,
)

app.autodiscover_tasks(["cybernexvpn.cybernexvpn_bot.tasks.tasks"])
