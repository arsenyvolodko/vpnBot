import json
import random

from aiogram.types import Message, CallbackQuery
from redis import RedisError

from cybernexvpn.cybernexvpn_bot import config
from cybernexvpn.cybernexvpn_bot.bot import models
from cybernexvpn.cybernexvpn_bot.bot.main import bot
from cybernexvpn.cybernexvpn_bot.bot.utils import new_text_storage
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.users import get_users
from cybernexvpn.cybernexvpn_bot.core.redis_config import r
from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.enums import ClientTypeEnum


async def send_safely(chat_id: int, text: str, **kwargs) -> bool:
    try:
        await bot.send_message(chat_id=chat_id, text=text, **kwargs)
        return True
    except Exception:
        return False


async def edit_safely(chat_id: int, message_id: int, text: str, **kwargs) -> bool:
    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, **kwargs)
        return True
    except Exception:
        return False


async def delete_message_or_delete_markup(obj):

    try:
        if isinstance(obj, Message):
            await obj.delete()
        else:
            await obj.delete_reply_markup()
        return True
    except Exception:
        return False


async def get_client_data(client: schemas.Client):
    return {
        "name": client.name,
        "status": (
            new_text_storage.ACTIVE if client.is_active else new_text_storage.INACTIVE
        ),
        "server": client.server.name,
        "price": client.price,
        "type": client.type.label,
        "auto_renew": "✅" if client.auto_renew else "❌",
        "date": client.end_date.strftime("%d.%m.%Y"),
    }


def generate_invitation_link(user_id: int) -> str:
    return f"{config.BOT_URL}?start={user_id}"


def save_payment_to_redis(url: str, payment: models.PaymentModel):
    payment_id = url.split("orderId=")[1]
    r.setex(payment_id, config.REDIS_DB_TTL, json.dumps(payment.model_dump()))


def get_payment_from_redis(payment_id: str) -> models.PaymentModel | None:
    payment = r.get(payment_id)
    if not payment:
        return
    return models.PaymentModel.parse_raw(payment)


def delete_payment_from_redis(payment_id: str):
    try:
        r.delete(payment_id)
    except RedisError:
        pass


async def check_user_balance_for_new_client(call: CallbackQuery, user: schemas.User, obj: schemas.Server | schemas.Client) -> bool:
    if user.balance < obj.price:
        await call.answer(
            new_text_storage.NOT_ENOUGH_MONEY_ERROR_MSG.format(user.balance),
            show_alert=True
        )
        return False
    return True


def get_filename(client: schemas.Client) -> str:
    base_name = "cybernexvpn"
    if client.type == ClientTypeEnum.ANDROID:
        base_name = random.choice(new_text_storage.ANDROID_NAME_CHOICES)
    tag = client.server.tag
    return f"{base_name}-{tag}.conf"
