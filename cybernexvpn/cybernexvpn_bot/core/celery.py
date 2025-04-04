import logging

from celery import Celery

from cybernexvpn.cybernexvpn_bot import config

logger = logging.getLogger(__name__)

REDIS_HOST = config.REDIS_HOST

app = Celery(
    "cybernexvpn.cybernexvpn_bot",
    broker=f"redis://{REDIS_HOST}:6379/0",
    backend=f"redis://{REDIS_HOST}:6379/1",
)

app.autodiscover_tasks(["cybernexvpn.cybernexvpn_bot.tasks.tasks"])
