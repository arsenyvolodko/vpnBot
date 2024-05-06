import subprocess

from vpnBot.wireguard_tools.exceptions.incompatible_keys_error import (
    IncompatibleKeysError,
)


class WireguardKeys:

    def __init__(self, **kwargs):

        if not kwargs:
            self.private_key = self.generate_private_key()
            self.public_key = self.generate_public_key(self.private_key)
            return

        self.private_key = kwargs.get("private_key", None)
        self.public_key = kwargs.get("public_key", None)

        if self.public_key and not self.private_key:
            raise IncompatibleKeysError()

        if self.private_key is not None and self.public_key:
            if self.generate_public_key(self.private_key) != self.public_key:
                raise IncompatibleKeysError()

        if self.private_key:
            self.public_key = self.generate_public_key(self.private_key)

    @staticmethod
    def generate_private_key() -> str:
        return subprocess.check_output(
            ["wg", "genkey"], text=True, stderr=subprocess.PIPE
        ).strip()

    @staticmethod
    def generate_public_key(private_key: str) -> str:
        return subprocess.check_output(
            ["wg", "pubkey"], text=True, input=private_key, stderr=subprocess.PIPE
        ).strip()

    @staticmethod
    def generate_preshared_key() -> str:
        return subprocess.check_output(
            ["wg", "genpsk"], text=True, stderr=subprocess.PIPE
        ).strip()
