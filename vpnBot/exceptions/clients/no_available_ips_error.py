from vpnBot.exceptions.clients.client_base_error import ClientBaseError
from vpnBot.consts.texts_storage import TextsStorage


class NoAvailableIpsError(ClientBaseError):
    def __init__(self, message: str = TextsStorage.NO_AVAILABLE_IPS_ERROR_MSG) -> None:
        self.message = message
        super().__init__(message)
