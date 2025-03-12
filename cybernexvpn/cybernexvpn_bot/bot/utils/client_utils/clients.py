from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient
from cybernexvpn.cybernexvpn_client.enums import ClientTypeEnum


async def get_client(user_id: int, client_id: int) -> schemas.Client:
    async with CyberNexVPNClient() as api_client:
        client: schemas.Client = await api_client.get_client(user_id, client_id)

    return client


async def get_user_clients(user_id: int) -> list[schemas.Client]:
    async with CyberNexVPNClient() as api_client:
        clients: list[schemas.Client] = await api_client.get_clients(user_id)

    return clients


async def create_client(user_id: int, server_id: int, client_type: ClientTypeEnum) -> schemas.Client:
    request_schema = schemas.CreateClientRequest(server=server_id, type=client_type)
    async with CyberNexVPNClient() as api_client:
        client: schemas.Client = await api_client.create_client(user_id, request_schema)

    return client


async def patch_client(user_id: int, client_id: int, **kwargs) -> schemas.Client:
    request_schema = schemas.PatchClientRequest(**kwargs)
    async with CyberNexVPNClient() as api_client:
        client: schemas.Client = await api_client.patch_client(user_id, client_id, request_schema)

    return client


async def delete_client(user_id: int, client_id: int) -> None:
    async with CyberNexVPNClient() as api_client:
        await api_client.delete_client(user_id, client_id)


async def get_config_file(user_id: int, client_id: int) -> str:
    async with CyberNexVPNClient() as api_client:
        config_file: str = await api_client.get_config_file(user_id, client_id)

    return config_file


async def reactivate_client(user_id: int, client_id: int) -> schemas.Client:
    async with CyberNexVPNClient() as api_client:
        client = await api_client.reactivate_client(user_id, client_id)
    return client
