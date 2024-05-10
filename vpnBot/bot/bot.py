import datetime

from aiogram import Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, CallbackQuery, Message

from vpnBot import config
from vpnBot.db.manager import db_manager
from vpnBot.db.tables import User
from vpnBot.keyboards.keyboards import *
from vpnBot.static.common import *
from vpnBot.static.texts_storage import *
from vpnBot.utils.bot_funcs import (
    add_and_get_user,
    get_user_balance,
    add_device_and_check_error,
    get_wg_client_by_client,
    send_config_and_qr,
    process_transaction,
)
from vpnBot.utils.files import delete_file
from vpnBot.utils.filters import MainMenuFilter
from vpnBot.wireguard_tools.wireguard_client import WireguardClient

dp = Dispatcher()
router = Router()
dp.include_router(router)


@dp.message(CommandStart())
async def welcome_message(message: Message):
    await message.answer(TextsStorage.START_TEXT, reply_markup=get_start_keyboard())
    await add_and_get_user(message)
    # todo check args and link


@router.callback_query(MainMenuFilter())
async def handle_callback(call: CallbackQuery):
    await call.message.edit_text(
        text=TextsStorage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )


@dp.callback_query(F.data == ButtonsStorage.DEVICES.callback)
async def handle_callback(call: CallbackQuery):
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
async def handle_query(call: CallbackQuery):
    user_balance = await get_user_balance(call.from_user.id)
    await call.message.edit_text(
        text=TextsStorage.ADD_DEVICE_CONFIRMATION_INFO.format(PRICE, user_balance),
        reply_markup=get_add_device_confirmation_keyboard(),
    )


@dp.callback_query(F.data == ButtonsStorage.ADD_DEVICE_CONFIRMATION.callback)
async def add_device_confirmed(call: CallbackQuery):
    if not (client := await add_device_and_check_error(call)):
        return
    wg_client = await get_wg_client_by_client(client)
    await send_config_and_qr(wg_client, call, client.device_num)


# noinspection PyTypeChecker
@router.callback_query(
    DevicesCallbackFactory.filter(F.callback == ButtonsStorage.DELETE_DEVICE.callback)
)
async def handle_specific_device_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    device_num = callback_data.device_num
    client = await db_manager.get_clint_by_user_id_and_device_num(
        call.from_user.id, device_num
    )
    try:
        await db_manager.delete_client(client)
        text = TextsStorage.DEVICE_SUCCESSFULLY_DELETED
    except Exception:
        text = TextsStorage.SOMETHING_WENT_WRONG_ERROR_MSG
    await call.message.edit_text(
        text,
        reply_markup=get_back_to_main_menu_keyboard(),
    )


# noinspection PyTypeChecker
@router.callback_query(
    DevicesCallbackFactory.filter(
        F.callback == ButtonsStorage.GET_DEVICES_CONFIG_AND_QR.callback
    )
)
async def handle_get_device_config_and_qr_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    device_num = callback_data.device_num
    client = await db_manager.get_clint_by_user_id_and_device_num(
        call.from_user.id, device_num
    )
    wg_client = await get_wg_client_by_client(client)
    await send_config_and_qr(wg_client, call, client.device_num)


# noinspection PyTypeChecker
@router.callback_query(
    DevicesCallbackFactory.filter(F.callback == ButtonsStorage.DEVICE.callback)
)
async def handle_specific_device_query(
    call: CallbackQuery, callback_data: DevicesCallbackFactory
):
    device_num = callback_data.device_num
    client = await db_manager.get_clint_by_user_id_and_device_num(
        call.from_user.id, device_num
    )
    status = TextsStorage.ACTIVE if client.active else TextsStorage.INACTIVE
    await call.message.edit_text(
        text=TextsStorage.SPECIFIC_DEVICE_INFO_TEXT.format(
            device_num, status, client.end_date.strftime("%d.%m.%Y")
        ),
        reply_markup=get_specific_device_keyboard(device_num),
    )


@router.callback_query(F.data == ButtonsStorage.FINANCE.callback)
async def handle_finance_callback(call: CallbackQuery):
    user_id = call.from_user.id
    user = await db_manager.get_record(User, user_id)
    await call.message.edit_text(
        TextsStorage.ON_YOUR_ACCOUNT.format(user.balance),
        reply_markup=get_finance_callback(),
    )


@router.callback_query(F.data == ButtonsStorage.GET_TRANSACTIONS_HISTORY.callback)
async def handle_get_transactions_query(call: CallbackQuery):
    user_id = call.from_user.id
    user: User = await db_manager.get_record(User, user_id)
    balance = user.balance
    cur_time = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M")
    text = TextsStorage.CURRENT_BALANCE.format(balance) + "\n\n"
    result = await db_manager.get_user_transactions(user_id)
    for transaction in result:
        cur_transaction = await process_transaction(transaction)
        text += cur_transaction + "\n\n"

    text += TextsStorage.ACTUAL_ON_MOMENT.format(cur_time)

    file_path = config.PATH_TO_CLIENTS_FILES / f"{user_id}_transactions_data.txt"
    with open(file_path, "w") as file:
        file.write(text)
        file.close()

    await call.bot.send_document(
        chat_id=call.from_user.id,
        document=FSInputFile(file_path, filename="Transactions.txt"),
    )

    await call.message.answer(
        TextsStorage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )

    await delete_file(file_path)


@router.callback_query(F.data == ButtonsStorage.FILL_UP_BALANCE.callback)
async def handle_fill_up_balance_query(call: CallbackQuery):
    await call.message.answer(
        TextsStorage.CHOOSE_SUM_TO_FILL_UP_BALANCE,
        reply_markup=get_fill_up_balance_keyboard()
    )


@router.callback_query(F.data == ButtonsStorage.PROMO_CODE.callback)
async def handle_promo_code_query(call: CallbackQuery, state: FSMContext = None):
    pass