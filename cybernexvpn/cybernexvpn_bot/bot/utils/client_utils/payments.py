from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery

from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.common import edit_with_error
from cybernexvpn.cybernexvpn_client import schemas, errors
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient


async def gen_payment_url(user_id: int, value: int, call: CallbackQuery | Message) -> str | None:
    try:
        async with CyberNexVPNClient() as api_client:
            request_schema = schemas.CreatePaymentRequest(value=value)
            payment_url_schema = await api_client.create_payment(user_id, request_schema)
            return payment_url_schema.url
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def get_transactions_history(user_id: int, call: CallbackQuery | Message) -> str | None:
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.get_transaction_history(user_id)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))
