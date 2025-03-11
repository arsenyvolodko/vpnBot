from vpnBot.db.manager import db_manager
from server.models import MessageModel
from cybernexvpn_bot.bot import bot
from vpnBot.config import MY_TG_ID, logger
from vpnBot.db.tables import User
from vpnBot.keyboards.keyboards import get_back_to_main_menu_keyboard
from vpnBot.utils.bot_funcs import send_message_safety


async def send_message_to_all(message: dict):
    message_model = MessageModel(**message)
    if message_model.only_to_me:
        user: User = await db_manager.get_record(User, id=MY_TG_ID)
        await send_message_safety(
            bot,
            user.id,
            text=message_model.text,
            reply_markup=get_back_to_main_menu_keyboard(with_new_message=True),
        )
        return
    users = await db_manager.get_records(User)
    for user in users:
        sent = await send_message_safety(
            bot,
            user.id,
            text=message_model.text,
            reply_markup=get_back_to_main_menu_keyboard(with_new_message=True),
        )
        if sent:
            logger.info(f"Message successfully sent to user {user}")
        else:
            logger.error(f"Error while sending message to user {user}")
