from aiogram.types import InlineKeyboardButton


class Button:

    def __init__(self) -> None:
        self.name = None
        self.txt = None
        self.callback_suffix: str = "_callback"

    def __str__(self):
        return self.callback

    @property
    def text(self):
        return self.txt

    @property
    def callback(self):
        return self.name.lower() + self.callback_suffix

    def get_button(self, **kwargs) -> InlineKeyboardButton:
        text = kwargs.get("text", self.txt)
        url = kwargs.get("url", None)
        if url:
            return InlineKeyboardButton(text=text, url=url)
        return InlineKeyboardButton(text=text, callback_data=self.callback)
