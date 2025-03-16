from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery

from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.common import edit_with_error
from cybernexvpn.cybernexvpn_client import schemas, errors
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient
from cybernexvpn.cybernexvpn_client.errors import NotFoundError


async def get_users(call: CallbackQuery | Message | None = None) -> list[schemas.User] | None:
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.get_users()
    except errors.ClientBaseError as e:
        if call:
            await edit_with_error(call, str(e))


async def get_user(user_id: int, call: CallbackQuery | Message) -> schemas.User | None:
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.get_user(user_id)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def create_user(user_id: int, username: str | None, call: CallbackQuery | Message) -> schemas.User | None:
    request_schema = schemas.CreateUserRequest(username=username)
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.create_user(user_id, request_schema)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def get_or_create_user(  # todo check using
    user_id: int, username: str | None, call: CallbackQuery | Message
) -> tuple[schemas.User | None, bool]:
    async with CyberNexVPNClient() as api_client:
        try:
            created = False
            user: schemas.User = await api_client.get_user(user_id)
        except NotFoundError:
            user = await create_user(user_id, username, call)
            created = True if user else False
    return user, created


async def apply_invitation_request(user_id: int, inviter_id: int, call: CallbackQuery | Message) -> bool | None:
    try:
        async with CyberNexVPNClient() as api_client:
            apply_invitation_request = schemas.ApplyInvitationRequest(inviter=inviter_id)
            await api_client.apply_invitation(user_id, apply_invitation_request)
            return True
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))
