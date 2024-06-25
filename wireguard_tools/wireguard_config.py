import asyncio
import subprocess
from pathlib import Path

from wireguard_tools.exceptions import ClientNotFoundError
from wireguard_tools.exceptions import SyncConfigError
from wireguard_tools.wireguard_client import WireguardClient
from wireguard_tools.wireguard_keys import WireguardKeys


class WireguardConfig:

    def __init__(self):
        self.interface: str | None = None
        self.private_key: str | None = None
        self.public_key: str | None = None
        self.endpoint: str | None = None
        self.config_path: Path | None = None
        self.sync_config_file_path: Path | None = None
        self.debug: bool = False

    def set_config(
        self,
        interface: str,
        private_key: str,
        endpoint: str,
        config_path: Path,
        sync_config_file_path: Path,
        **kwargs,
    ):
        if not all(
            (interface, private_key, endpoint, config_path, sync_config_file_path)
        ):
            raise ValueError("Config params cannot be None.")
        self.interface = interface
        self.private_key = private_key
        self.public_key = WireguardKeys.generate_public_key(private_key)
        self.endpoint = endpoint
        self.config_path = config_path
        self.debug = kwargs.get("debug", False)

    async def add_client(self, client: WireguardClient):
        new_data = self._gen_client_data(client)
        with open(self.config_path, "a") as file:
            file.write(new_data)
            file.close()
        if not self.debug:
            await self._sync_config()

    async def remove_client(self, client: WireguardClient):
        data_to_delete = self._gen_client_data(client)
        old_data = await self._get_data_from_server_file()

        new_data = old_data.replace(data_to_delete, "", 1)
        if new_data == old_data:
            if data_to_delete not in old_data:
                return
            raise ClientNotFoundError("Client not found")

        with open(self.config_path, "w") as file:
            file.write(new_data)
        if not self.debug:
            await self._sync_config()

    async def _get_data_from_server_file(self) -> str:
        with open(self.config_path, "r") as file:
            data = file.read()
        return data

    @staticmethod
    def _gen_client_data(client: WireguardClient) -> str:
        new_data = ""
        new_data += f"### Client {client.name}\n"
        new_data += "[Peer]\n"
        new_data += f"PublicKey = {client.keys.public_key}\n"
        new_data += f"AllowedIPs = {client.ipv4}\n"
        new_data += "\n"
        return new_data

    async def _sync_config(self):
        try:
            subprocess.run(
                [self.interface],
                check=True,
                capture_output=True,
                text=True
            )
        except Exception:
            raise SyncConfigError()
