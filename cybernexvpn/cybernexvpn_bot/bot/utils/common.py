from aiogram.types import Message

from cybernexvpn.cybernexvpn_bot import config
from cybernexvpn.cybernexvpn_bot.bot.main import bot
from cybernexvpn.cybernexvpn_bot.bot.utils import new_text_storage
from cybernexvpn.cybernexvpn_client import schemas


async def send_safely(chat_id: int, text: str, **kwargs) -> bool:
    try:
        await bot.send_message(chat_id=chat_id, text=text, **kwargs)
        return True
    except Exception:
        return False


async def delete_message_or_delete_markup(obj):

    if isinstance(obj, Message):
        await obj.delete()
        return

    await obj.delete_reply_markup()


def get_auto_renew_emoji(status: bool):
    return "✅" if status else "❌"


async def get_client_data(client: schemas.Client):
    return {
        "name": client.name,
        "status": new_text_storage.ACTIVE if client.is_active else new_text_storage.INACTIVE,
        "server": client.server_name,
        "price": client.price,
        "type": client.type.label,
        "auto_renew": get_auto_renew_emoji(client.auto_renew),
        "date": client.end_date.strftime("%d.%m.%Y")
    }


def generate_invitation_link(user_id: int) -> str:
    return f"{config.BOT_URL}?start={user_id}"
