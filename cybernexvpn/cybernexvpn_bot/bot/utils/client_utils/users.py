import logging

from aiogram.types import Message, User as TgUser
from aiogram.types.callback_query import CallbackQuery

from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.common import edit_with_error
from cybernexvpn.cybernexvpn_client import schemas, errors
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient
from cybernexvpn.cybernexvpn_client.errors import NotFoundError

logger = logging.getLogger(__name__)


async def _sync_user_profile(
    api_client: CyberNexVPNClient, user: schemas.User, tg_user: TgUser
) -> schemas.User:
    updates = {}
    if user.username != tg_user.username:
        updates["username"] = tg_user.username
    if user.first_name != tg_user.first_name:
        updates["first_name"] = tg_user.first_name
    if not updates:
        return user
    try:
        return await api_client.patch_user(user.id, schemas.PatchUserRequest(**updates))
    except errors.ClientBaseError:
        logger.exception("Failed to sync user profile for %s", user.id)
        return user


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
            user = await api_client.get_user(user_id)
            return await _sync_user_profile(api_client, user, call.from_user)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def create_user(
    user_id: int,
    username: str | None,
    first_name: str | None,
    call: CallbackQuery | Message,
) -> schemas.User | None:
    request_schema = schemas.CreateUserRequest(username=username, first_name=first_name)
    try:
        async with CyberNexVPNClient() as api_client:
            return await api_client.create_user(user_id, request_schema)
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))


async def get_or_create_user(
    user_id: int,
    username: str | None,
    first_name: str | None,
    message: CallbackQuery | Message,
) -> tuple[schemas.User | None, bool]:
    async with CyberNexVPNClient() as api_client:
        try:
            created = False
            user: schemas.User = await api_client.get_user(user_id)
            user = await _sync_user_profile(api_client, user, message.from_user)
        except NotFoundError:
            user = await create_user(user_id, username, first_name, message)
            created = True if user else False
        except errors.ClientBaseError as e:
            await edit_with_error(message, str(e))
            return None, False

    return user, created


async def apply_invitation_request(user_id: int, inviter_id: int, call: CallbackQuery | Message) -> bool | None:
    try:
        async with CyberNexVPNClient() as api_client:
            apply_invitation_request = schemas.ApplyInvitationRequest(inviter=inviter_id)
            await api_client.apply_invitation(user_id, apply_invitation_request)
            return True
    except errors.ClientBaseError as e:
        await edit_with_error(call, str(e))
