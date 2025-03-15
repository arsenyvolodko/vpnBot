from cybernexvpn.cybernexvpn_bot.bot.utils import new_text_storage


class ClientBaseError(Exception):
    def __init__(self, message: str | None = None, *args: object) -> None:
        self.message = message or new_text_storage.SOMETHING_WENT_WRONG_ERROR_MSG
        super().__init__(*args)

    def __str__(self):
        return self.message
