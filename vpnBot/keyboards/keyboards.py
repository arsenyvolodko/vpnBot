from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from vpnBot.db.tables import Client
from vpnBot.keyboards.button import Button
from vpnBot.keyboards.buttons_storage import ButtonsStorage
from vpnBot.consts.common import FILLING_UP_VALUES
from vpnBot.consts.texts_storage import TextsStorage
from vpnBot.keyboards.factories import (
    FillUpBalanceFactory,
    DevicesCallbackFactory,
)


def _construct_keyboard(*args, **kwargs) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [button.get_button() if isinstance(button, Button) else button]
        for button in args
    ]
    if kwargs.get("with_back_to_menu", None):
        inline_keyboard.append([ButtonsStorage.GO_BACK_TO_MAIN_MENU.get_button()])
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_start_keyboard(from_start=False) -> InlineKeyboardMarkup:
    return _construct_keyboard(
        ButtonsStorage.WG_APP_IOS.get_button(url=TextsStorage.WG_APP_IOS_LINK),
        ButtonsStorage.WG_APP_ANDROID.get_button(url=TextsStorage.WG_APP_ANDROID_LINK),
        ButtonsStorage.WG_APP_PC.get_button(url=TextsStorage.WG_APP_PC_LINK),
        (
            ButtonsStorage.GO_TO_MAIN_MENU_FROM_START
            if from_start
            else ButtonsStorage.GO_TO_MAIN_MENU
        ),
    )


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return _construct_keyboard(
        ButtonsStorage.DEVICES,
        ButtonsStorage.FINANCE,
        ButtonsStorage.PROMO_CODE,
        # ButtonsStorage.INVITATION_LINK,
    )


def get_back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    return _construct_keyboard(with_back_to_menu=True)


def get_cancel_state_keyboard() -> InlineKeyboardMarkup:
    return _construct_keyboard(ButtonsStorage.CANCEL_STATE)


def _get_device_button_text(device: Client) -> str:
    status = "🟢" if device.active else "🔴"
    return f"{ButtonsStorage.DEVICE.text.format(device.device_num)} {status}"


def get_add_device_confirmation_keyboard() -> InlineKeyboardMarkup:
    return _construct_keyboard(
        ButtonsStorage.ADD_DEVICE_CONFIRMATION.get_button(),
        ButtonsStorage.DEVICES.get_button(text=ButtonsStorage.GO_BACK.text),
    )


def get_delete_device_confirmation_keyboard(device_num: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=ButtonsStorage.DELETE_DEVICE_CONFIRMATION.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.DELETE_DEVICE_CONFIRMATION.callback,
            device_num=device_num,
        ),
    )
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.DEVICE.callback, device_num=device_num
        ),
    )
    builder.adjust(1)
    return builder.as_markup()


def get_finance_callback() -> InlineKeyboardMarkup:
    return _construct_keyboard(
        ButtonsStorage.GET_TRANSACTIONS_HISTORY,
        ButtonsStorage.FILL_UP_BALANCE,
        ButtonsStorage.GO_BACK_TO_MAIN_MENU,
    )


def get_devices_keyboard(
    devices: list[Client], add_new_allowed: bool
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for device in devices:
        builder.button(
            text=_get_device_button_text(device),
            callback_data=DevicesCallbackFactory(
                callback=ButtonsStorage.DEVICE.callback, device_num=device.device_num
            ),
        )
    if add_new_allowed:
        builder.button(
            text=ButtonsStorage.ADD_DEVICE.text,
            callback_data=ButtonsStorage.ADD_DEVICE.callback,
        )
    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback,
    )
    builder.adjust(1)
    return builder.as_markup()


def get_specific_device_keyboard(device_num: int, status: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if status:
        builder.button(
            text=ButtonsStorage.GET_DEVICES_CONFIG_AND_QR.text,
            callback_data=DevicesCallbackFactory(
                callback=ButtonsStorage.GET_DEVICES_CONFIG_AND_QR.callback,
                device_num=device_num,
            ),
        )
    else:
        builder.button(
            text=ButtonsStorage.RESUME_DEVICE_SUBSCRIPTION.text,
            callback_data=DevicesCallbackFactory(
                callback=ButtonsStorage.RESUME_DEVICE_SUBSCRIPTION.callback,
                device_num=device_num,
            ),
        )
    builder.button(
        text=ButtonsStorage.DELETE_DEVICE.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.DELETE_DEVICE.callback,
            device_num=device_num,
        ),
    )
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=ButtonsStorage.DEVICES.callback,
    )
    builder.adjust(1)
    return builder.as_markup()


def get_fill_up_balance_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for balance_value in FILLING_UP_VALUES:
        builder.button(
            text=str(balance_value) + "₽",
            callback_data=FillUpBalanceFactory(
                value=balance_value,
            ),
        )
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=ButtonsStorage.FINANCE.callback,
    )
    builder.adjust(3, 3, 1)
    return builder.as_markup()


def get_payment_url_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=TextsStorage.PAY,
        url=payment_url
    )
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=ButtonsStorage.FINANCE.callback,
    )
    builder.adjust(1)
    return builder.as_markup()
