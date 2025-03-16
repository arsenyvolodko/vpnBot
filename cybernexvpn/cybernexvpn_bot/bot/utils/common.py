import json

from aiogram.types import Message, CallbackQuery

from cybernexvpn.cybernexvpn_bot import config
from cybernexvpn.cybernexvpn_bot.bot import models
from cybernexvpn.cybernexvpn_bot.bot.main import bot
from cybernexvpn.cybernexvpn_bot.bot.utils import new_text_storage
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.users import get_users
from cybernexvpn.cybernexvpn_bot.core.redis_config import r
from cybernexvpn.cybernexvpn_client import schemas


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
        "server": client.server_name,
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


async def send_message_from_admin_util(message_schema):
    if message_schema.only_to_me:
        await send_safely(config.ADMIN_USER_ID, message_schema.text, parse_mode="HTML")
    else:
        users = await get_users()
        if not users:
            return

        for user in users:
            await send_safely(user.id, message_schema.text, parse_mode="HTML")


async def handle_payment_succeeded_util(payment_id: str):
    payment = get_payment_from_redis(payment_id)
    if not payment:
        return
    await bot.edit_message_text(
        chat_id=payment.user_id,
        message_id=payment.message_id,
        text=new_text_storage.PAYMENT_SUCCESSFULLY_PROCESSED.format(payment.value),
        parse_mode="HTML",
    )


async def check_user_balance_for_new_client(call: CallbackQuery, user: schemas.User, obj: schemas.Server | schemas.Client) -> bool:
    if user.balance < obj.price:
        await call.answer(
            new_text_storage.NOT_ENOUGH_MONEY_ERROR_MSG.format(user.balance),
            show_alert=True
        )
        return False
    return True
