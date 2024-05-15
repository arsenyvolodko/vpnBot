from wireguard_tools.exceptions.wireguard_base_error import WireguardBaseError


class ClientNotFoundError(WireguardBaseError):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
