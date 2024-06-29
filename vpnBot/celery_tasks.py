from celery_config import celery_app
from vpnBot.bot.main import loop
from vpnBot.utils.payments import fill_up_balance
from vpnBot.utils.renew_subscription import renew_subscription_func
from vpnBot.utils.send_message_to_everyone import send_message_to_all


@celery_app.task
def renew_subscription_task():
    loop.run_until_complete(renew_subscription_func())


@celery_app.task
def send_message_to_everyone(message: dict):
    loop.run_until_complete(send_message_to_all(message))


@celery_app.task
def process_payment(payment):
    loop.run_until_complete(fill_up_balance(payment))
