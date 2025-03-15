from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery

from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.common import edit_with_error
from cybernexvpn.cybernexvpn_client import schemas, errors
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient


async def get_servers(call: CallbackQuery | Message) -> list[schemas.Server] | None:
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.get_servers()
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def get_server(server_id: int, call: CallbackQuery | Message) -> schemas.Server | None:
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.get_server(server_id)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))
