from pathlib import Path

import qrcode

from wireguard_tools.wireguard_keys import WireguardKeys


class WireguardClient:

    def __init__(
            self, name: str, ipv4: str, ipv6: str, keys: WireguardKeys, endpoint: str, server_public_key: str
    ):
        if not all((name, ipv4, ipv6, keys, endpoint, server_public_key)):
            raise ValueError("Config params cannot be None.")
        self.name = name
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.keys = keys
        self.endpoint = endpoint
        self.server_public_key = server_public_key

    async def gen_qr_config(self, dir_path: Path) -> Path:
        file_path = await self._gen_path(dir_path, f"{self.name}.png")
        config_data = self._get_config()
        img = qrcode.make(config_data)
        img.save(str(file_path))
        return file_path

    async def gen_text_config(self, dir_path: Path) -> Path:
        file_path = await self._gen_path(dir_path, f"{self.name}.conf")
        with file_path.open("w") as file:
            config_data = self._get_config()
            file.write(config_data)
        return file_path

    @staticmethod
    async def _gen_path(path: Path, file_name: str) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        file_path = path / file_name

        with open(file_path, "a"):
            pass

        return file_path

    def _get_config(self) -> str:
        config_data = ""
        config_data += "[Interface]\n"
        config_data += f"PrivateKey = {self.keys.private_key}\n"
        config_data += f"Address = {self.ipv4}, {self.ipv6}\n"
        config_data += "DNS = 1.1.1.1, 1.0.0.1\n"
        config_data += "\n"
        config_data += "[Peer]\n"
        config_data += f"PublicKey = {self.server_public_key}\n"
        config_data += f"Endpoint = {self.endpoint}\n"
        config_data += "AllowedIPs = 0.0.0.0/0, ::/0\n"
        return config_data
