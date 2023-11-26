import qrcode
from Client import Client
from DateFunc import DateFunc
from constants import *
from subprocess import call


class Files:

    @classmethod
    def make_qr_code_png(cls, file_data, path):
        img = qrcode.make(file_data)
        img.save(path)

    @classmethod
    def create_client_config_file(cls, client: Client):
        file_data = cls.gen_data_for_client_config_file(client)

        base_path = f'{PATH_TO_CLIENTS_FILES}/{client.user_id}_{client.device_num}'
        config_file_path = f'{base_path}.conf'
        qr_code_file_path = f'{base_path}' + '_qr.png'

        with open(config_file_path, 'w') as file:
            file.write(file_data)
            file.close()

        cls.make_qr_code_png(file_data, qr_code_file_path)
        return config_file_path, qr_code_file_path

    @classmethod
    def update_server_config_file(cls, client: Client):
        new_data = cls.gen_data_for_server_config_file(client)
        with open(PATH_TO_CONFIG, 'a') as file:
            file.write(new_data)
            file.close()
        cls.run_bash_sync_script()
        return True

    @classmethod
    def gen_data_for_client_config_file(cls, client: Client):
        file_data = ''
        file_data += '[Interface]\n'
        file_data += f'PrivateKey = {client.keys.private_key}\n'
        file_data += f'Address = {client.ips.get_ipv4(True)}, {client.ips.get_ipv6(True)}\n'
        file_data += 'DNS = 1.1.1.1, 1.0.0.1\n'
        file_data += '\n'
        file_data += '[Peer]\n'
        file_data += 'PublicKey = IzVzdvd3012NmM4wBeUNnbUyukPtroX4oScY/2YFlU4=\n'
        file_data += f'PresharedKey = {client.keys.preshared_key}\n'
        file_data += 'Endpoint = 91.201.113.17:63906\n'
        file_data += 'AllowedIPs = 0.0.0.0/0, ::/0\n'
        return file_data

    @classmethod
    def gen_data_for_server_config_file(cls, client: Client):
        new_data = ''
        new_data += f"### Client {client.get_client_name()}\n"
        new_data += '[Peer]\n'
        new_data += f'PublicKey = {client.keys.public_key}\n'
        new_data += f'PresharedKey = {client.keys.preshared_key}\n'
        new_data += f'AllowedIPs = {client.ips.get_ipv4(True)}, {client.ips.get_ipv6(True)}\n'
        new_data += '\n'
        return new_data

    @classmethod
    def add_client(cls, client: Client):
        cls.create_client_config_file(client)
        cls.update_server_config_file(client)

    @classmethod
    def get_data_from_server_file(cls):
        data = ''
        with open(PATH_TO_CONFIG, 'r') as file:
            for line in file:
                data += line
            file.close()
        return data

    @classmethod
    def make_back_up_copy(cls, data: str = None):
        if not data:
            data = cls.get_data_from_server_file()
        cur_time = DateFunc.get_cur_time("%d-%m-%Y-%H-%M-%S")
        with open(f'{PATH_TO_META}/meta{cur_time}.conf', 'w') as meta_file:
            meta_file.write(data)
            meta_file.close()

    @classmethod
    def remove_client(cls, client: Client):
        data_to_delete = cls.gen_data_for_server_config_file(client)
        old_data = cls.get_data_from_server_file()

        new_data = old_data.replace(data_to_delete, '', 1)
        if new_data == old_data:
            return False
        with open(PATH_TO_CONFIG, 'w') as file:
            file.write(new_data)
        cls.run_bash_sync_script()
        return True

    @classmethod
    def write_to_logs(cls, text: str, comment: str = None):
        cur_time = DateFunc.get_cur_time()
        with open(PATH_TO_LOGS, 'a') as logs:
            if comment:
                logs.write(f'{cur_time}, ({comment}): {text}\n')
            else:
                logs.write(f'{cur_time}, {text}\n')

    @classmethod
    def run_bash_sync_script(cls):
        rc = call("./sync_inter.sh")
