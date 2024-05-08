import subprocess
from pathlib import Path

from vpnBot.config import DEBUG
from vpnBot.wireguard_tools.exceptions.client_not_found_error import ClientNotFoundError
from vpnBot.wireguard_tools.exceptions.sync_config_error import SyncConfigError
from vpnBot.wireguard_tools.wireguard_client import WireguardClient


class WireguardConfig:

    def __init__(self):
        self.interface: str | None = None
        self.public_key: str | None = None
        self.endpoint: str | None = None
        self.config_path: Path | None = None

    def set_config(
        self, interface: str, public_key: str, endpoint: str, config_path: Path
    ):
        if not all((interface, public_key, endpoint, config_path)):
            raise ValueError("Config params cannot be None.")
        self.interface = interface
        self.public_key = public_key
        self.endpoint = endpoint
        self.config_path = config_path

    def add_client(self, client: WireguardClient):
        new_data = self._gen_client_data(client)
        with open(self.config_path, "a") as file:
            file.write(new_data)
            file.close()
        if not DEBUG:
            self._sync_config()

    def remove_client(self, client: WireguardClient):
        data_to_delete = self._gen_client_data(client)
        old_data = self._get_data_from_server_file()

        new_data = old_data.replace(data_to_delete, "", 1)
        if new_data == old_data:
            raise ClientNotFoundError("Client not found")

        with open(self.config_path, "w") as file:
            file.write(new_data)
        if not DEBUG:
            self._sync_config()

    def _get_data_from_server_file(self) -> str:
        with open(self.config_path, "r") as file:
            data = file.read()
        return data

    @staticmethod
    def _gen_client_data(client: WireguardClient) -> str:
        new_data = ""
        new_data += f"### Client {client.name}\n"
        new_data += "[Peer]\n"
        new_data += f"PublicKey = {client.keys.private_key}\n"
        allowed_ips = f"{client.ipv4}, {client.ipv6}" if client.ipv6 else client.ipv4
        new_data += f"AllowedIPs = {allowed_ips}\n"
        new_data += "\n"
        return new_data

    def _sync_config(self):
        try:
            cmd = f"wg syncconf {self.interface} {self.config_path}"
            subprocess.run(cmd, shell=True)
        except Exception as e:
            raise SyncConfigError(e)
