import logging

from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery

from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.common import edit_with_error
from cybernexvpn.cybernexvpn_client import schemas, errors
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient
from cybernexvpn.cybernexvpn_client.enums import ClientTypeEnum

logger = logging.getLogger(__name__)


async def get_client(user_id: int, client_id: int, call: CallbackQuery | Message) -> schemas.Client | None:
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.get_client(user_id, client_id)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def get_user_clients(user_id: int, call: CallbackQuery | Message) -> list[schemas.Client] | None:
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.get_clients(user_id)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def create_client(
    user_id: int, server_id: int, client_type: ClientTypeEnum, call: CallbackQuery | Message
) -> schemas.Client | None:
    request_schema = schemas.CreateClientRequest(server=server_id, type=client_type)
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.create_client(user_id, request_schema)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def patch_client(user_id: int, client_id: int, call: CallbackQuery | Message, **kwargs) -> schemas.Client | None:
    request_schema = schemas.PatchClientRequest(**kwargs)
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.patch_client(
                user_id, client_id, request_schema
            )
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def delete_client(user_id: int, client_id: int, call: CallbackQuery | Message) -> bool | None:
    try:
        async with CyberNexVPNClient() as api_client:
            await api_client.delete_client(user_id, client_id)
            return True
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def get_config_file(user_id: int, client_id: int, call: CallbackQuery | Message) -> str | None:
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.get_config_file(user_id, client_id)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def reactivate_client(user_id: int, client_id: int, call: CallbackQuery | Message) -> schemas.Client | None:
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.reactivate_client(user_id, client_id)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))
