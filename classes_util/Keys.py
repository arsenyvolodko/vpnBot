import subprocess


class IncompatibleKeysError(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Keys:
    def __init__(self, private_key: str = None, public_key: str = None, preshared_key: str = None):

        if not public_key:
            self.private_key = private_key if private_key else self.generate_private_key()
            self.public_key = self.generate_public_key(self.private_key)
            self.preshared_key = preshared_key if preshared_key else self.generate_preshared_key()
            return

        if self.generate_public_key(private_key) != public_key:
            raise IncompatibleKeysError()

        self.private_key = private_key
        self.public_key = public_key
        self.preshared_key = preshared_key

    @staticmethod
    def generate_private_key():
        return subprocess.check_output(["wg", "genkey"], text=True, stderr=subprocess.PIPE).strip()

    @classmethod
    def generate_public_key(cls, private_key: str):
        return subprocess.check_output(["wg", "pubkey"], text=True, input=private_key,
                                       stderr=subprocess.PIPE).strip()

    @staticmethod
    def generate_preshared_key():
        return subprocess.check_output(["wg", "genpsk"], text=True, stderr=subprocess.PIPE).strip()
