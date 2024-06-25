from aiogram.filters import Filter
from aiogram.types import CallbackQuery

from vpnBot.keyboards.buttons_storage import ButtonsStorage


class MainMenuFilter(Filter):
    async def __call__(self, call: CallbackQuery) -> bool:
        return (
            call.data == ButtonsStorage.GO_TO_MAIN_MENU.callback
            or call.data == ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback
            or call.data == ButtonsStorage.GO_TO_MAIN_MENU_FROM_START.callback
            or call.data == ButtonsStorage.GO_BACK_TO_MAIN_MENU_WITH_NEW_MESSAGE.callback
        )
