import os
import uuid
from pathlib import Path
from typing import Any

from aiogram.types import CallbackQuery, FSInputFile, Message
from yookassa import Payment
from yookassa.domain.response import PaymentResponse

from vpnBot import config
from vpnBot.config import BOT_TG_URL
from vpnBot.consts.common import INVITATION_BONUS
from vpnBot.consts.texts_storage import TextsStorage
from vpnBot.db import db_manager
from vpnBot.db.tables import User, Transaction, Client, Ips
from vpnBot.enums import TransactionCommentEnum
from vpnBot.enums.operation_type_enum import OperationTypeEnum
from vpnBot.keyboards.keyboards import (
    get_back_to_main_menu_keyboard,
    get_main_menu_keyboard,
)
from wireguard_tools.wireguard_client import WireguardClient


async def send_message_safety(bot, user_id: int, text: str, **kwargs) -> bool:
    try:
        await bot.send_message(text=text, chat_id=user_id, **kwargs)
        return True
    except Exception:
        return False


async def delete_message_or_delete_markup(message: Message):
    try:
        await message.delete()
    except Exception:
        await message.delete_reply_markup()


async def get_user_balance(user_id: int):
    user = await db_manager.get_record(User, id=user_id)
    return user.balance


async def get_wg_client_by_client(client: Client) -> WireguardClient:
    wg_keys = (await db_manager.get_keys_by_client_id(client.id)).get_as_wg_keys()
    ips = await db_manager.get_record(Ips, client_id=client.id)
    wg_config = config.WIREGUARD_CONFIG_MAP[ips.interface]
    wg_client = WireguardClient(
        name=f"{client.user_id}_{client.device_num}",
        ipv4=ips.ipv4,
        keys=wg_keys,
        endpoint=wg_config.endpoint,
        server_public_key=wg_config.public_key,
    )
    return wg_client


async def send_config_and_qr(
    wg_client: WireguardClient, call: CallbackQuery, device_num: int
) -> None:
    qr_file = await wg_client.gen_qr_config(config.PATH_TO_CLIENTS_FILES)
    config_file = await wg_client.gen_text_config(config.PATH_TO_CLIENTS_FILES)
    await delete_message_or_delete_markup(call.message)

    file_name = str(uuid.uuid4())

    await call.bot.send_document(
        chat_id=call.from_user.id,
        document=FSInputFile(config_file, filename=f"{file_name}.conf"),
    )

    await call.bot.send_photo(
        call.from_user.id,
        photo=FSInputFile(qr_file),
        caption=TextsStorage.INSTRUCTION,
        parse_mode="HTML",
    )

    await call.bot.send_message(
        call.from_user.id,
        text=TextsStorage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )

    await delete_file(qr_file)
    await delete_file(config_file)


async def process_transaction(transaction: Transaction) -> str:
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


def generate_invitation_link(user_id: int) -> str:
    return f"{config.BOT_TG_URL}?start={user_id}"


async def check_invitation(message: Message, inviter_id: Any) -> bool | None:
    try:
        inviter_id = int(inviter_id)
        inviter = await db_manager.get_record(User, id=inviter_id)
        if not inviter or message.from_user.id == inviter.id:
            return

        await db_manager.update_balance(
            user_id=inviter_id,
            value=INVITATION_BONUS,
            op_type=OperationTypeEnum.INCREASE,
            comment=TransactionCommentEnum.INVITATION,
        )

        await message.bot.send_message(
            chat_id=inviter_id,
            text=TextsStorage.SUCCESSFUL_INVITATION_INFO_MSG,
            reply_markup=get_back_to_main_menu_keyboard(),
        )

        return True

    except ValueError:
        return


def create_payment(value: int) -> PaymentResponse:
    payment = Payment.create(
        {
            "amount": {"value": f"{value}.00", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": BOT_TG_URL,
            },
            "capture": True,
            "description": f"Пополнение баланса на {value} рублей",
            "customer": {"email": "arvolodko@gmail.com"},
        }
    )
    return payment


async def delete_file(path: Path):
    if path.exists():
        try:
            os.remove(path)
        except Exception:
            pass
