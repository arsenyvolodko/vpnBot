import subprocess


def generate_keys():
    private_key = subprocess.check_output(['wg', 'genkey'], text=True, stderr=subprocess.PIPE).strip()
    public_key = subprocess.check_output(['wg', 'pubkey'], text=True, input=private_key, stderr=subprocess.PIPE).strip()
    preshared_key = subprocess.check_output(['wg', 'genpsk'], text=True, stderr=subprocess.PIPE).strip()
    return private_key, public_key, preshared_key


# def generate_next_ip(last_ip: str):
#     last_ip_list = last_ip.split('.')
#     last_val = int(last_ip_list[-1])
#     if last_val != 255:
#         last_ip_list[-1] = str(last_val + 1)
#     else:
#         if int(last_ip_list[-2]) == 255:
#             raise IndexError("No more free ip addresses available")
#         last_ip_list[-2] = str(int(last_ip_list[-2]) + 1)
#         last_ip_list[-1] = '0'
#     new_ip = '.'.join(last_ip_list)
#     return new_ip


def generate_next_ip(last_ip: str):
    last_ip_list = last_ip.split('.')
    new_val = int(last_ip_list[-1]) + 1
    if new_val == 256:
        raise IndexError("No more free ip addresses available")
    else:
        new_ipv4 = f'10.66.66.{new_val}'
        new_ipv6 = f'fd42:42:42::{new_val}'
    return new_ipv4, new_ipv6




def create_client_config_file(file_name: str, private_key, preshared_key: str, new_ips: list):
    with open (f'client_files/{file_name}.conf', 'w') as file:
        file.write('[Interface]\n')
        file.write(f'PrivateKey = {private_key}\n')
        file.write(f'Address = {new_ips[0]}, {new_ips[1]}\n')
        file.write('DNS = 1.1.1.1, 1.0.0.1\n')
        file.write('\n')
        file.write('[Peer]\n')
        file.write('PublicKey = IzVzdvd3012NmM4wBeUNnbUyukPtroX4oScY/2YFlU4=\n')
        file.write(f'PresharedKey = {preshared_key}\n')
        file.write('Endpoint = 91.201.113.17:63906\n')
        file.write('AllowedIPs = 0.0.0.0/0, ::/0\n')
        file.close()


def update_server_config_file(client_name: str, public_key: str, preshared_key: str, new_ips: list):
    with open(f'some_dir/server.conf', 'a') as file:
        file.write(f"### Client {client_name}\n")
        file.write('[Peer]\n')
        file.write(f'PublicKey = {public_key}\n')
        file.write(f'PresharedKey = {preshared_key}\n')
        file.write(f'AllowedIPs = {new_ips[0]}, {new_ips[1]}\n')
        file.write('\n')
        file.close()


def add_client(client_name: str, last_ip: str):
    private_key, public_key, preshared_key = generate_keys()
    new_ips = list(generate_next_ip(last_ip))
    new_ips[0] += '/32'
    new_ips[1] += '/128'
    create_client_config_file(client_name, private_key, preshared_key, new_ips)
    update_server_config_file(client_name, public_key, preshared_key, new_ips)
    return new_ips


last_ip = '10.66.66.10'
last_val_ip = last_ip
last_ip = add_client(f'client{11}', last_ip)[0].strip('./32')
