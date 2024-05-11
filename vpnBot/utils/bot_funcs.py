from aiogram import types
from aiogram.types import CallbackQuery, FSInputFile, Message

from vpnBot import config
from vpnBot.db.manager import db_manager
from vpnBot.db.tables import User, Transaction, Client
from vpnBot.enums import TransactionCommentEnum
from vpnBot.enums.operation_type_enum import OperationTypeEnum
from vpnBot.exceptions.clients import *
from vpnBot.exceptions.clients.client_base_error import ClientBaseError
from vpnBot.exceptions.promo_codes import *
from vpnBot.exceptions.promo_codes.promo_code_base_error import PromoCodeBaseError
from vpnBot.keyboards.keyboards import (
    get_back_to_main_menu_keyboard,
    get_main_menu_keyboard,
)
from vpnBot.static.common import DEVICES_MAX_AMOUNT, PRICE
from vpnBot.static.texts_storage import TextsStorage
from vpnBot.utils.files import delete_file
from vpnBot.wireguard_tools.wireguard_client import WireguardClient


async def add_and_get_user(message: types.Message):
    # user = await db_manager.get_user_by_id(message.from_user.id)
    user = await db_manager.get_record(User, message.from_user.id)
    if not user:
        new_user = User(id=message.from_user.id, username=message.from_user.username)
        user = await db_manager.add_record(new_user)
        new_record = Transaction(
            user_id=user.id,
            value=PRICE,
            operation_type=OperationTypeEnum.INCREASE,
            comment=TransactionCommentEnum.START_BALANCE,
        )
        await db_manager.add_record(new_record)
    return user


async def get_user_balance(user_id: int):
    # user = await db_manager.get_user_by_id(user_id)
    user = await db_manager.get_record(User, user_id)
    return user.balance


async def get_user_devices_amount(user_id: int):
    devices = await db_manager.get_user_devices(user_id)
    return len(devices)


async def _check_devices_and_balance(devices_num: int, user_balance: int):
    if devices_num == DEVICES_MAX_AMOUNT:
        raise DevicesLimitError()
    if user_balance < PRICE:
        raise NotEnoughMoneyError()


async def get_wg_client_by_client(client: Client) -> WireguardClient:
    wg_keys = (await db_manager.get_keys_by_client_id(client.id)).get_as_wg_keys()
    ips = await db_manager.get_ips_by_client_id(client.id)
    wg_client = WireguardClient(
        name=f"{client.user_id}_{client.device_num}",
        ipv4=ips.ipv4,
        ipv6=ips.ipv6,
        keys=wg_keys,
        endpoint=config.SERVER_ENDPOINT,
    )
    return wg_client


async def send_config_and_qr(
    wg_client: WireguardClient, call: CallbackQuery, device_num: int
):
    qr_file = wg_client.gen_qr_config(config.PATH_TO_CLIENTS_FILES)
    config_file = wg_client.gen_text_config(config.PATH_TO_CLIENTS_FILES)
    await call.message.delete()

    await call.bot.send_document(
        chat_id=call.from_user.id,
        document=FSInputFile(config_file, filename=f"NexVpn{device_num}.conf"),
    )

    await call.bot.send_photo(call.from_user.id, photo=FSInputFile(qr_file))

    await call.bot.send_message(
        call.from_user.id,
        text=TextsStorage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )

    await delete_file(qr_file)
    await delete_file(config_file)


async def process_transaction(transaction: Transaction):
    time = transaction.operation_time.strftime("%d.%m.%Y, %H:%M")
    text = f"{time}\n"
    text += "Операция: "
    text += (
        "списание "
        if transaction.operation_type == OperationTypeEnum.DECREASE
        else "пополнение "
    )
    text += str(transaction.value) + "₽\n"
    text += f"Комментарий: {transaction.comment.value}"
    return text
