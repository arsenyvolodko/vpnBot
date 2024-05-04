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

    def get_button(self, *args, **kwargs) -> InlineKeyboardButton:
        text = kwargs.get('text', self.txt)
        url = kwargs.get('url', None)
        if url:
            return InlineKeyboardButton(text=text, url=url)
        callback = f"{self.callback}#{'#'.join(map(str, args))}" if args else self.callback
        return InlineKeyboardButton(text=text, callback_data=callback)

    def has_callback(self, received_callback: str):
        return received_callback.startswith(self.callback)
