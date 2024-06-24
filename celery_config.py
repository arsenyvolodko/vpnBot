from celery import Celery

# from celery.schedules import crontab
# from vpnBot import celery_tasks  # do not clear

celery_app = Celery(
    "vpnBot", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)

celery_app.autodiscover_tasks(["vpnBot.celery_tasks"])
