from cybernexvpn.cybernexvpn_client.errors.client_base_error import ClientBaseError


class InvalidRequestDataError(ClientBaseError):
    def __init__(self, message=''):
        self.message = message
