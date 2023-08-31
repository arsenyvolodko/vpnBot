from Ips import Ips
from Keys import Keys

class NoSuchClientExistsError(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Client:

    def __init__(self, user_id: int, device_num: int, ips: Ips, keys: Keys = None, end_date: str = None):
        self.user_id = user_id
        self.device_num = device_num
        self.ips = ips
        self.end_date = end_date
        if not keys:
            self.keys = Keys()
        else:
            self.keys = keys

    def __repr__(self):
        data = f'user_id: {self.user_id},\n' \
               f'device_num: {self.device_num},\n' \
               f'ipv4: {self.ips.get_ipv4(True)},\n' \
               f'ipv6: {self.ips.get_ipv6(True)},\n' \
               f'private_key: {self.keys.private_key},\n' \
               f'public_key: {self.keys.public_key},\n' \
               f'preshared_key: {self.keys.preshared_key},\n' \
               f'end_date: {self.end_date}'
        return data

    def get_client_name(self):
        return f'{self.user_id}_{self.device_num}'

    def get_path_to_config(self):
        return 'client_files/' + self.get_client_name() + '.conf'


