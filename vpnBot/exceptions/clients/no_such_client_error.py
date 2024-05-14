from vpnBot.exceptions.clients.client_base_error import ClientBaseError
from vpnBot.consts.texts_storage import TextsStorage


class NoSuchClientError(ClientBaseError):
    def __init__(self, message: str = TextsStorage.NO_SUCH_CLIENT_ERROR_MSG) -> None:
        self.message = message
        super().__init__(message)
