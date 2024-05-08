from aiogram import Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile

from vpnBot import config
from vpnBot.db.manager import db_manager
from vpnBot.keyboards.keyboards import *
from vpnBot.static.common import *
from vpnBot.static.texts_storage import *
from vpnBot.utils.bot_funcs import (
    add_and_get_user,
    get_user_balance,
    add_device_and_check_error,
)
from vpnBot.utils.files import delete_file
from vpnBot.wireguard_tools.wireguard_client import WireguardClient

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
    F.data
    == ButtonsStorage.GO_TO_MAIN_MENU.callback
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
        text=(
            TextsStorage.CHOOSE_DEVICE
            if user_devices
            else TextsStorage.NO_DEVICES_ADDED
        ),
        reply_markup=get_devices_keyboard(
            user_devices, len(user_devices) < DEVICES_MAX_AMOUNT
        ),
    )


@dp.callback_query(F.data == ButtonsStorage.ADD_DEVICE.callback)
async def handle_query(call: types.CallbackQuery):
    user_balance = await get_user_balance(call.from_user.id)
    await call.message.edit_text(
        text=TextsStorage.ADD_DEVICE_CONFIRMATION_INFO.format(user_balance),
        reply_markup=get_add_device_confirmation_keyboard(),
    )


@dp.callback_query(F.data == ButtonsStorage.ADD_DEVICE_CONFIRMATION.callback)
async def add_device_confirmed(call: types.CallbackQuery):
    if not (client := await add_device_and_check_error(call)):
        return
    wg_keys = (await db_manager.get_keys_by_client_id(client.id)).get_as_wg_keys()
    ips = await db_manager.get_ips_by_client_id(client.id)
    wg_client = WireguardClient(
        name=f"{client.user_id}_{client.device_num}",
        ipv4=ips.ipv4,
        ipv6=ips.ipv6,
        keys=wg_keys,
        endpoint=config.SERVER_ENDPOINT,
    )
    qr_file = wg_client.gen_qr_config(config.PATH_TO_CLIENTS_FILES)
    config_file = wg_client.gen_text_config(config.PATH_TO_CLIENTS_FILES)
    await call.message.delete()

    await call.bot.send_document(
        chat_id=call.from_user.id,
        document=FSInputFile(config_file, filename=f"NexVpn{client.device_num}.conf"),
    )

    await call.bot.send_photo(call.from_user.id, photo=FSInputFile(qr_file))

    await call.bot.send_message(
        call.from_user.id,
        text=TextsStorage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )

    delete_file(qr_file)
    delete_file(config_file)
