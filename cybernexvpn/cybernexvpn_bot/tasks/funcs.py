import logging

from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.users import get_users
from cybernexvpn.cybernexvpn_bot.bot.utils.common import send_safely
from cybernexvpn.cybernexvpn_bot import config
from cybernexvpn.cybernexvpn_bot.tasks import schemas

logger = logging.getLogger(__name__)


async def send_message_from_admin_util(message_schema: schemas.Message):
    if message_schema.only_to_me:
        await send_safely(config.ADMIN_USER_ID, message_schema.text, parse_mode="HTML")
    else:
        users = await get_users()
        logging.info(f"Sending message to {len(users)} users")
        for user in users:
            await send_safely(user.id, message_schema.text, parse_mode="HTML")
