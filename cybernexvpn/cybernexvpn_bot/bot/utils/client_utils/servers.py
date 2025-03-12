from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient


async def get_servers() -> list[schemas.Server]:
    async with CyberNexVPNClient() as api_client:
        servers = await api_client.get_servers()

    return servers


async def get_server(server_id: int) -> schemas.Server | None:
    servers = await get_servers()
    for server in servers:
        if server.id == server_id:
            return server
    return None
