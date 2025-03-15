from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel

from cybernexvpn.cybernexvpn_bot.bot.utils import new_text_storage
from cybernexvpn.cybernexvpn_bot.config import FILLING_UP_VALUES
from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_bot.bot.keyboards.button import Button
from cybernexvpn.cybernexvpn_bot.bot.keyboards.buttons_storage import ButtonsStorage
from cybernexvpn.cybernexvpn_client.enums import ClientTypeEnum
from cybernexvpn.cybernexvpn_bot.bot.keyboards.factories import (
    FillUpBalanceFactory,
    DevicesCallbackFactory,
    ServersCallbackFactory,
    AddDeviceFactory,
    EditDeviceTypeCallbackFactory,
)


def _construct_keyboard(*args, **kwargs) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [button.get_button() if isinstance(button, Button) else button]
        for button in args
    ]
    if kwargs.get("with_back_to_menu"):
        if kwargs.get("with_new_message"):
            inline_keyboard.append(
                [ButtonsStorage.GO_BACK_TO_MAIN_MENU_WITH_NEW_MESSAGE.get_button()]
            )
        else:
            inline_keyboard.append([ButtonsStorage.GO_BACK_TO_MAIN_MENU.get_button()])
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_choose_device_type_keyboard(**kwargs) -> InlineKeyboardMarkup:
    if server := kwargs.get("server"):
        builder = _get_choose_device_type_util(
            server, AddDeviceFactory, ButtonsStorage.SERVER, ServersCallbackFactory
        )
    else:
        client = kwargs.get("client")
        builder = _get_choose_device_type_util(
            client,
            EditDeviceTypeCallbackFactory,
            ButtonsStorage.DEVICE,
            DevicesCallbackFactory,
        )

    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback,
    )
    builder.adjust(3, 2)
    return builder.as_markup()


def _get_choose_device_type_util(
    obj_with_id: BaseModel,
    type_factory: type[CallbackData],
    return_button: Button,
    return_factory: type[CallbackData],
):
    builder = InlineKeyboardBuilder()

    for client_type in ClientTypeEnum:
        if client_type == ClientTypeEnum.UNKNOWN:
            continue

        builder.button(
            text=client_type.label,  # noqa
            callback_data=type_factory(
                id=obj_with_id.id, type=client_type.value  # noqa
            ),
        )

    print("AAAA", return_button, return_button.text, return_button.callback, obj_with_id.id)
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=return_factory(
            callback=return_button.callback, id=obj_with_id.id
        ),
    )

    return builder


def get_first_usage_keyboard() -> InlineKeyboardMarkup:
    return _construct_keyboard(
        ButtonsStorage.ADD_DEVICE.get_button(text="Подключить VPN"),
    )


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return _construct_keyboard(
        ButtonsStorage.DEVICES,
        ButtonsStorage.FINANCE,
        ButtonsStorage.PROMO_CODE,
        ButtonsStorage.INVITATION_LINK,
    )


def get_servers_keyboard(servers: list[schemas.Server]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for server in servers:
        builder.button(
            text=server.name,
            callback_data=ServersCallbackFactory(
                callback=ButtonsStorage.SERVER.callback,
                id=server.id,
            ),
        )
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=ButtonsStorage.DEVICES.callback,
    )
    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback,
    )
    builder.adjust(*[1] * len(servers), 2)
    return builder.as_markup()


def get_devices_keyboard(clients: list[schemas.Client]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for client in clients:
        builder.button(
            text=_get_client_button_text(client),
            callback_data=DevicesCallbackFactory(
                callback=ButtonsStorage.DEVICE.callback,
                id=client.id,
            ),
        )
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


def get_back_to_main_menu_keyboard(**kwargs) -> InlineKeyboardMarkup:
    return _construct_keyboard(with_back_to_menu=True, **kwargs)


def get_cancel_state_keyboard() -> InlineKeyboardMarkup:
    return _construct_keyboard(ButtonsStorage.CANCEL_STATE)


def _get_client_button_text(client: schemas.Client) -> str:
    status = "🟢" if client.is_active else "🔴"
    return f"{client.name} {status}"


def get_add_device_confirmation_keyboard() -> InlineKeyboardMarkup:
    return _construct_keyboard(
        ButtonsStorage.ADD_DEVICE_CONFIRMATION.get_button(),
        ButtonsStorage.DEVICES.get_button(text=ButtonsStorage.GO_BACK.text),
    )


def get_delete_device_confirmation_keyboard(
    client: schemas.Client,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=ButtonsStorage.DELETE_DEVICE_CONFIRMATION.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.DELETE_DEVICE_CONFIRMATION.callback,
            id=client.id,
        ),
    )
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.EDIT_DEVICE.callback, id=client.id
        ),
    )
    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback,
    )
    builder.adjust(1, 2)
    return builder.as_markup()


def get_finance_callback() -> InlineKeyboardMarkup:
    return _construct_keyboard(
        ButtonsStorage.GET_TRANSACTIONS_HISTORY,
        ButtonsStorage.FILL_UP_BALANCE,
        ButtonsStorage.GO_BACK_TO_MAIN_MENU,
    )


def get_specific_server_keyboard(server: schemas.Server):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=ButtonsStorage.CONTINUE.text,
        callback_data=AddDeviceFactory(
            id=server.id,
        ),
    )
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=ButtonsStorage.ADD_DEVICE.callback,
    )
    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback,
    )
    builder.adjust(1, 2)
    return builder.as_markup()


def get_specific_device_keyboard(client: schemas.Client) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if client.is_active:
        builder.button(
            text=ButtonsStorage.GET_DEVICES_CONFIG_AND_QR.text,
            callback_data=DevicesCallbackFactory(
                callback=ButtonsStorage.GET_DEVICES_CONFIG_AND_QR.callback,
                id=client.id,
            ),
        )
    else:
        builder.button(
            text=ButtonsStorage.REACTIVATE_DEVICE.text,
            callback_data=DevicesCallbackFactory(
                callback=ButtonsStorage.REACTIVATE_DEVICE.callback, id=client.id
            ),
        )

    builder.button(
        text=ButtonsStorage.EDIT_DEVICE.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.EDIT_DEVICE.callback, id=client.id
        ),
    )
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=ButtonsStorage.DEVICES.callback,
    )
    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback,
    )
    builder.adjust(1, 1, 2)
    return builder.as_markup()


def get_edit_device_keyboard(client: schemas.Client) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=ButtonsStorage.EDIT_DEVICE_NAME.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.EDIT_DEVICE_NAME.callback,
            id=client.id,
        ),
    )
    if client.is_active:
        builder.button(
            text=ButtonsStorage.EDIT_DEVICE_AUTO_RENEW.text.format(
                "✅" if client.auto_renew else "❌"
            ),
            callback_data=DevicesCallbackFactory(
                callback=ButtonsStorage.EDIT_DEVICE_AUTO_RENEW.callback,
                id=client.id,
            ),
        )
    builder.button(
        text=ButtonsStorage.EDIT_DEVICE_TYPE.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.EDIT_DEVICE_TYPE.callback,
            id=client.id,
        ),
    )
    builder.button(
        text=ButtonsStorage.DELETE_DEVICE.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.DELETE_DEVICE.callback,
            id=client.id,
        ),
    )
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=DevicesCallbackFactory(
            callback=ButtonsStorage.DEVICE.callback,
            id=client.id,
        ),
    )
    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback,
    )
    buttons_cnt = 4 if client.is_active else 3
    builder.adjust(*[1] * buttons_cnt, 2)
    return builder.as_markup()


def get_fill_up_balance_keyboard(from_admin=False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    filling_up_values = FILLING_UP_VALUES.copy()
    if from_admin:
        filling_up_values.insert(0, 5)

    for balance_value in filling_up_values:
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
    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback,
    )
    builder.adjust(1, 3, 3, 2) if from_admin else builder.adjust(3, 3, 2)
    return builder.as_markup()


def get_payment_url_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=new_text_storage.TO_PAY_BTN_LINK_TEXT, url=payment_url)
    builder.button(
        text=ButtonsStorage.GO_BACK.text,
        callback_data=ButtonsStorage.FILL_UP_BALANCE.callback,
    )
    builder.button(
        text=ButtonsStorage.GO_BACK_TO_MAIN_MENU.text,
        callback_data=ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback,
    )
    builder.adjust(1, 2)
    return builder.as_markup()
