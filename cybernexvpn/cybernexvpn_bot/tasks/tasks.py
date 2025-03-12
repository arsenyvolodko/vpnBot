import logging

from cybernexvpn.cybernexvpn_bot.tasks import schemas
from cybernexvpn.cybernexvpn_bot.bot.main import loop
from cybernexvpn.cybernexvpn_bot.core.celery import app
from cybernexvpn.cybernexvpn_bot.tasks.funcs import send_message_from_admin_util

logger = logging.getLogger(__name__)


@app.task
def send_message_from_admin(request_dict: schemas.Message):
    message = schemas.Message.model_validate(request_dict)
    logger.info(f"Sending message from admin: {message}")
    return loop.run_until_complete(send_message_from_admin_util(message))
