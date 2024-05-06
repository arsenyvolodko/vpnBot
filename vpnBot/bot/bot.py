from aiogram import Dispatcher, Router, F
from aiogram.filters import CommandStart

from vpnBot.db.manager import db_manager
from vpnBot.exceptions.devices_limit_error import DevicesLimitError
from vpnBot.exceptions.no_available_ips_error import NoAvailableIpsError
from vpnBot.exceptions.not_enough_money_error import NotEnoughMoneyError
from vpnBot.keyboards.keyboards import *
from vpnBot.static.common import *
from vpnBot.static.texts_storage import *
from vpnBot.utils.bot_funcs import add_and_get_user, get_user_balance, add_device

dp = Dispatcher()
router = Router()
dp.include_router(router)


@dp.message(CommandStart())
async def welcome_message(message: types.Message):
    await message.answer(TextsStorage.START_TEXT, reply_markup=get_start_keyboard())
    await add_and_get_user(message)
    # todo check args and link


@dp.callback_query(
    # F.data in [
    #     ButtonsStorage.GO_TO_MAIN_MENU.callback,
    #     ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback
    # ]
    F.data == ButtonsStorage.GO_TO_MAIN_MENU.callback
    # F.data == ButtonsStorage.GO_BACK_TO_MAIN_MENU.callback
)
async def handle_callback(call: types.CallbackQuery):
    await call.message.edit_text(
        text=TextsStorage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )


@dp.callback_query(
    F.data == ButtonsStorage.DEVICES.callback
)
async def handle_callback(call: types.CallbackQuery):
    user_devices = await db_manager.get_user_devices(call.from_user.id)
    await call.message.edit_text(
        text=TextsStorage.CHOOSE_DEVICE if user_devices else TextsStorage.NO_DEVICES_ADDED,
        reply_markup=get_devices_keyboard(user_devices, len(user_devices) < DEVICES_MAX_AMOUNT)
    )


@dp.callback_query(
    F.data == ButtonsStorage.ADD_DEVICE.callback
)
async def handle_query(call: types.CallbackQuery):
    user_balance = await get_user_balance(call.from_user.id)
    await call.message.edit_text(
        text=TextsStorage.ADD_DEVICE_CONFIRMATION_INFO.format(user_balance),
        reply_markup=get_add_device_confirmation_keyboard()
    )


@dp.callback_query(
    F.data == ButtonsStorage.ADD_DEVICE_CONFIRMATION
)
async def add_device_confirmed(call: types.CallbackQuery):
    if not (client := await add_device_and_check_error(call)):
        return


async def add_device_and_check_error(call: types.CallbackQuery) -> Client | None:
    try:
        client = await add_device(call.from_user.id)
        return client
    except DevicesLimitError:
        error_text = TextsStorage.ADD_DEVICE_CONFIRMATION_INFO
    except NoAvailableIpsError:
        error_text = TextsStorage.NO_AVAILABLE_IPS_ERROR_MSG
    except NotEnoughMoneyError:
        error_text = TextsStorage.NOT_ENOUGH_MONEY_ERROR_MSG
    except Exception:
        error_text = TextsStorage.SOMETHING_WENT_WRONG_ERROR_MSG
        # todo add logs here

    await call.message.answer(
        text=error_text,
        reply_markup=get_back_to_main_menu_keyboard()
    )
    return None
