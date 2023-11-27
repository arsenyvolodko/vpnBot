from aiogram import types
from aiogram.types import InlineKeyboardButton

from constants import *


def get_button(text, callback):
    return types.InlineKeyboardButton(text=text, callback_data=callback)


BACK_TO_MAIN_MENU_BTN = get_button(BACK_TO_MAIN_MENU_TEXT, BACK_TO_MAIN_MENU_CALLBACK)


def get_color_by_device_action(active: int):
    return '🟢' if active else '🔴'


def get_main_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(DEVICES_TEXT, DEVICES_CALLBACK))
    keyboard.add(get_button(FINANCE_TEXT, FINANCE_CALLBACK))
    keyboard.add(get_button(PROMOCODES_TEXT, PROMOCODES_CALLBACK))
    keyboard.add(get_button(INVITING_LINKS_TEXT, INVITING_LINKS_CALLBACK))
    return keyboard


def get_back_to_previous_menu(callback: str):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(BACK_TO_PREV_MENU_TEXT, callback))
    return keyboard


def get_devices_keyboard(devices: list):
    keyboard = types.InlineKeyboardMarkup()
    # devices = botDB.get_user_devices(user_id)
    devices.sort(key=lambda x: x[0])
    for i in devices:
        keyboard.add(
            get_button(f"Устройство №{i[0]} {get_color_by_device_action(i[1])}", f"specific_device_callback#{i[0]}"))
    if len(devices) < 3:
        keyboard.add(get_button(ADD_DEVICE_TEXT, ADD_DEVICE_CALLBACK))
    keyboard.add(BACK_TO_MAIN_MENU_BTN)
    return keyboard


def get_add_device_confirmation_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(BACK_TO_PREV_MENU_TEXT, DEVICES_CALLBACK),
                 get_button(CONTINUE_TEXT, ADD_DEVICE_CONFIRMED_CALLBACK))
    return keyboard


def get_specific_device_keyboard(active: bool):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(GET_QR_AND_CONFIG_TEXT, GET_QR_AND_CONFIG_CALLBACK))
    keyboard.add(get_button(DELETE_DEVICE_TEXT, DELETE_DEVICE_CALLBACK))
    if not active:
        keyboard.add(get_button(EXTEND_SUBSCRIPTION_FOR_DEVICE_TEXT, EXTEND_SUBSCRIPTION_FOR_DEVICE_CALLBACK))
    keyboard.add(get_button(BACK_TO_PREV_MENU_TEXT, DEVICES_CALLBACK))
    return keyboard


def get_delete_device_confirmation_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(DELETE_DEVICE_CONFIRM_TEXT, DELETE_DEVICE_CONFIRM_CALLBACK))
    keyboard.add(get_button(DELETE_DEVICE_CANCEL_TEXT, DEVICES_CALLBACK))
    return keyboard


def get_not_enough_money_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(BACK_TO_PREV_MENU_TEXT, DEVICES_CALLBACK))
    keyboard.add(get_button(FILL_UP_TEXT, FILL_UP_CALLBACK))
    keyboard.add(BACK_TO_MAIN_MENU_BTN)
    return keyboard


def to_main_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Android', url=WG_APP_ANDROID_LINK))
    keyboard.add(InlineKeyboardButton('iOS', url=WG_APP_IOS_LINK))
    keyboard.add(InlineKeyboardButton('PC', url=WG_APP_PC_LINK))
    keyboard.add(get_button("Перейти в меню", BACK_TO_MAIN_MENU_CALLBACK))
    return keyboard


def get_back_to_main_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(BACK_TO_MAIN_MENU_BTN)
    return keyboard


def get_finance_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(PAYMENTS_HISTORY_TEXT, PAYMENTS_HISTORY_CALLBACK))
    keyboard.add(get_button(FILL_UP_TEXT, FILL_UP_CALLBACK))
    keyboard.add(BACK_TO_MAIN_MENU_BTN)
    return keyboard


def get_extend_subscription_confirmation_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(CONTINUE_TEXT, EXTEND_SUBSCRIPTION_FOR_DEVICE_CONFIRM_CALLBACK),
                 get_button(BACK_TO_PREV_MENU_TEXT, DEVICES_CALLBACK))
    return keyboard


def get_fill_up_balance_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(FILL_UP_BALANCE_100_TEXT, FILL_UP_BALANCE_100_CALLBACK),
                 get_button(FILL_UP_BALANCE_200_TEXT, FILL_UP_BALANCE_200_CALLBACK),
                 get_button(FILL_UP_BALANCE_300_TEXT, FILL_UP_BALANCE_300_CALLBACK))
    keyboard.add(get_button(FILL_UP_BALANCE_500_TEXT, FILL_UP_BALANCE_500_CALLBACK),
                 get_button(FILL_UP_BALANCE_700_TEXT, FILL_UP_BALANCE_700_CALLBACK),
                 get_button(FILL_UP_BALANCE_1000_TEXT, FILL_UP_BALANCE_1000_CALLBACK))
    keyboard.add(get_button(BACK_TO_PREV_MENU_TEXT, FINANCE_CALLBACK))
    return keyboard


def get_back_to_previous_menu_from_callbacks_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(get_button(BACK_TO_PREV_MENU_TEXT, BACK_TO_PREV_MENU_FROM_PROMO_CALLBACK))
