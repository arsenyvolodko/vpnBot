import logging

from cybernexvpn.cybernexvpn_bot.bot.utils.common import (
    send_message_from_admin_util,
    handle_payment_succeeded_util,
)
from cybernexvpn.cybernexvpn_bot.tasks import schemas
from cybernexvpn.cybernexvpn_bot.bot.main import loop
from cybernexvpn.cybernexvpn_bot.core.celery import app

logger = logging.getLogger(__name__)


@app.task
def send_message_from_admin(request_dict: schemas.Message):
    message = schemas.Message.model_validate(request_dict)
    logger.info(f"Sending message from admin task: {message}")
    return loop.run_until_complete(send_message_from_admin_util(message))


@app.task
def handle_payment_succeeded(payment_id: str):
    logger.info(f"Handling payment succeeded task: {payment_id}")
    return loop.run_until_complete(handle_payment_succeeded_util(payment_id))
