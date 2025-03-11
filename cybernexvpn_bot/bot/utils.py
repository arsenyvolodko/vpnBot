from aiogram.types import Message

from cybernexvpn_bot import config, new_text_storage
from cybernexvpn_bot.new_text_storage import ACTIVE
from cybernexvpn_client import schemas


async def send_safely(bot, chat_id, text, **kwargs):
    try:
        await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except Exception:
        pass


async def delete_message_or_delete_markup(obj):

    if isinstance(obj, Message):
        await obj.delete()
        return

    await obj.delete_reply_markup()


def get_auto_renew_emoji(status: bool):
    return "✅" if status else "❌"


async def _get_client_data(client: schemas.Client):
    return {
        "name": client.name,
        "status": ACTIVE if client.is_active else new_text_storage.INACTIVE,
        "server": client.server_name,
        "price": client.price,
        "type": client.type.label,
        "auto_renew": get_auto_renew_emoji(client.auto_renew),
        "date": client.end_date.strftime("%d.%m.%Y")
    }


def generate_invitation_link(user_id: int) -> str:
    return f"{config.BOT_URL}?start={user_id}"
