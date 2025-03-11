from cybernexvpn_bot import config
from cybernexvpn_bot.bot.utils import send_safely
from cybernexvpn_bot.new_text_storage import SUCCESSFUL_INVITATION_INFO_MSG
from cybernexvpn_client import schemas
from cybernexvpn_client.client import CyberNexVPNClient
from cybernexvpn_client.errors import NotFoundError, ClientBaseError


async def get_user(user_id: int) -> schemas.User:
    async with CyberNexVPNClient() as api_client:
        user: schemas.User = await api_client.get_user(user_id)

    return user


async def get_or_create_user(user_id: int, username: str | None = None) -> tuple[schemas.User, bool]:
    async with CyberNexVPNClient() as api_client:
        try:
            created = False
            user: schemas.User = await api_client.get_user(user_id)
        except NotFoundError:
            created = True
            create_user_request = schemas.CreateUserRequest(
                username=username
            )
            user: schemas.User = await api_client.create_user(user_id, create_user_request)

    return user, created


async def check_and_apply_invitation(bot, user: schemas.User, args: str) -> None:

    try:
        inviter_id = int(args)
        print(inviter_id)
        async with CyberNexVPNClient() as api_client:
            apply_invitation_request = schemas.ApplyInvitationRequest(
                inviter=inviter_id
            )
            await api_client.apply_invitation(user.id, apply_invitation_request)
    except ValueError | ClientBaseError:
        return

    print("AA", inviter_id)
    await send_safely(
        bot,
        chat_id=inviter_id,
        text=SUCCESSFUL_INVITATION_INFO_MSG.format(
            f"@{user.username}" if user.username else "",
        ),
    )
