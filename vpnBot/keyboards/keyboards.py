from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from vpnBot.db.tables import Client
from vpnBot.keyboards.buttons_storage import ButtonsStorage
from vpnBot.keyboards.fabrics.devices_callback_factory import DevicesCallbackFactory
from vpnBot.static.texts_storage import TextsStorage


def get_start_keyboard() -> types.InlineKeyboardMarkup:
    inline_keyboard = [
        [ButtonsStorage.WG_APP_ANDROID.get_button(url=TextsStorage.WG_APP_ANDROID_LINK)],
        [ButtonsStorage.WG_APP_IOS.get_button(url=TextsStorage.WG_APP_IOS_LINK)],
        [ButtonsStorage.WG_APP_PC.get_button(url=TextsStorage.WG_APP_PC_LINK)],
        [ButtonsStorage.GO_TO_MAIN_MENU.get_button()]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# def construct_keyboard_with_builder(factory, *args):
#     builder = InlineKeyboardBuilder()
#     for btn, value in args:
#         builder.button(
#             text=btn.text,
#             callback_data=factory(callback=btn.callback, value=value)
#         )
#     return builder.as_markup()


def construct_keyboard(*args, **kwargs):
    # factory = kwargs.get('factory', None)
    # if factory:
    #     return construct_keyboard_with_builder(factory, *args)
    inline_keyboard = [[button.get_button()] for button in args]
    if kwargs.get("with_back_to_menu", None):
        inline_keyboard.append([ButtonsStorage.GO_BACK_TO_MAIN_MENU.get_button()])
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_main_menu_keyboard():
    return construct_keyboard(
        ButtonsStorage.DEVICES, ButtonsStorage.FINANCE,
        ButtonsStorage.PROMO_CODE, ButtonsStorage.INVITATION_LINK,
        with_back_to_menu=True
    )


def get_back_to_main_menu_keyboard():
    return construct_keyboard(with_back_to_menu=True)


def get_device_button_text(device: Client):
    status = '🟢' if device.active else '🔴'
    return f'{ButtonsStorage.DEVICE.text.format(device.device_num)} {status}'


def get_devices_keyboard(devices: list[Client], add_new_allowed: bool):
    builder = InlineKeyboardBuilder()
    for device in devices:
        builder.button(
            text=get_device_button_text(device),
            callback_data=DevicesCallbackFactory(
                callback=ButtonsStorage.DEVICE.callback,
                device_num=device.device_num
            )
        )
    if add_new_allowed:
        builder.button(
            text=ButtonsStorage.ADD_DEVICE.text,
            callback_data=ButtonsStorage.ADD_DEVICE.callback
        )
    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback
    )
    builder.adjust(1)
    return builder.as_markup()


def get_add_device_confirmation_keyboard():
    inline_keyboard = [
        [ButtonsStorage.ADD_DEVICE_CONFIRMATION.get_button()],
        [ButtonsStorage.DEVICES.get_button(text=ButtonsStorage.GO_BACK.text)]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
