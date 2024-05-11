from vpnBot.exceptions.promo_codes.promo_code_base_error import PromoCodeBaseError
from vpnBot.static.texts_storage import TextsStorage


class PromoCodeInactiveError(PromoCodeBaseError):
    def __init__(
        self, message: str = TextsStorage.PROMO_CODE_INACTIVE_ERROR_MSG
    ) -> None:
        self.message = message
        super().__init__(message)
