from aiogram import Dispatcher, Router, F
from aiogram.filters import CommandStart

from vpnBot.db.manager import db_manager
from vpnBot.keyboards.keyboards import *
from vpnBot.static.texts_storage import *
from vpnBot.utils.bot_funcs import add_and_get_user, get_user_balance

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


@dp.callback_query(F.data == ButtonsStorage.DEVICES.callback)
async def handle_callback(call: types.CallbackQuery):
    user_devices = await db_manager.get_user_devices(call.from_user.id)
    await call.message.edit_text(
        text=TextsStorage.CHOOSE_DEVICE if user_devices else TextsStorage.NO_DEVICES_ADDED,
        reply_markup=get_devices_keyboard(user_devices)
    )


# noinspection PyTypeChecker
@dp.callback_query(DevicesCallbackFactory.filter(
    F.callback == ButtonsStorage.ADD_DEVICE.callback)
)
async def handle_query(call: types.CallbackQuery):
    user_balance = await get_user_balance(call.from_user.id)
    await call.message.edit_text(
        text=TextsStorage.ADD_DEVICE_CONFIRMATION_INFO.format(user_balance),
        reply_markup=get_add_device_confirmation_keyboard()
    )

