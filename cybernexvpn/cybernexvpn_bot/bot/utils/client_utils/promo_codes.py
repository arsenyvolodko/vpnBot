from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery

from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.common import edit_with_error
from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient
from cybernexvpn.cybernexvpn_client.errors import ClientBaseError


async def apply_promo_code(
    user_id: int, promo_code: str, call: CallbackQuery | Message
) -> schemas.ApplyPromoCodeResponse | None:
    try:
        async with CyberNexVPNClient() as api_client:
            request_schema = schemas.ApplyPromoCodeRequest(code=promo_code)
            return await api_client.apply_promo_code(user_id, request_schema)

    except ClientBaseError as e:
        await edit_with_error(call, str(e))
