from datetime import datetime
import qrcode
from Client import Client
from Ips import Ips
from Keys import Keys

class Files:

    @classmethod
    def make_qr_code_png(cls, file_data, path):
        img = qrcode.make(file_data)
        img.save(path)


    @classmethod
    def get_user_id_from_client_name(cls, client_name: str, string_type: bool = False):
        if string_type:
            return client_name.split('_')[0]
        return int(client_name.split('_')[0])


    @classmethod
    def create_client_config_file(cls, client: Client):
        file_data = cls.gen_data_for_server_config_file(client)

        base_path = f'client_files/{client.user_id}_{client.device_num}'
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
        cls.make_back_up_copy()
        with open(f'some_dir/server.conf', 'a') as file:
            file.write(new_data)
            file.close()


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
        with open('some_dir/server.conf', 'r') as file:
            for line in file:
                data += line
            file.close()
        return data


    @classmethod
    def make_back_up_copy(cls, data: str = None):
        if not data:
            data = cls.get_data_from_server_file()
        cur_time = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        with open(f'some_dir/meta{cur_time}.conf', 'w') as meta_file:
            meta_file.write(data)
            meta_file.close()


    @classmethod
    def remove_client(cls, client: Client):
        data_to_delete = cls.gen_data_for_server_config_file(client)
        old_data = cls.get_data_from_server_file()
        cls.make_back_up_copy(old_data)

        new_data = old_data.replace(data_to_delete, '', 1)
        with open(f'some_dir/server.conf', 'w') as file:
            file.write(new_data)
            file.close()
            return True



ips = Ips('10.66.66.13/32')
keys = Keys('mFw2SoHeJACsQCeaufjx7biaTUwK3lOlaRBWXHwUO3I=', '5I3vAh/Z8nOlB70KtHrPUR3KjbUSiZMTnfigw9WmEWw=', 'EBS7ushP9suGXlsBe3zECED2sOWAtbwAy94I5bRaAWY=')
client = Client(123456789, 2, ips, keys, '30.08.2023')
# client = Client(1234567, 1, ips, keys, '30.08.2023')
# add_client(client)
# delete_client(client)