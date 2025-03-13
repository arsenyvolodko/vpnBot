from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient
from cybernexvpn.cybernexvpn_client.errors import NotFoundError


async def get_users() -> list[schemas.User]:
    async with CyberNexVPNClient() as api_client:
        users: list[schemas.User] = await api_client.get_users()

    return users


async def get_user(user_id: int) -> schemas.User:
    async with CyberNexVPNClient() as api_client:
        user: schemas.User = await api_client.get_user(user_id)

    return user


async def get_or_create_user(
    user_id: int, username: str | None = None
) -> tuple[schemas.User, bool]:
    async with CyberNexVPNClient() as api_client:
        try:
            created = False
            user: schemas.User = await api_client.get_user(user_id)
        except NotFoundError:
            created = True
            create_user_request = schemas.CreateUserRequest(username=username)
            user: schemas.User = await api_client.create_user(
                user_id, create_user_request
            )

    return user, created


async def apply_invitation_request(user_id: int, inviter_id: int) -> None:
    async with CyberNexVPNClient() as api_client:
        apply_invitation_request = schemas.ApplyInvitationRequest(inviter=inviter_id)
        await api_client.apply_invitation(user_id, apply_invitation_request)
