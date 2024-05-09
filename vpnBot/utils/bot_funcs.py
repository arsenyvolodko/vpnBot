from aiogram import types

from vpnBot.db.manager import db_manager
from vpnBot.db.tables import User, Transaction, Client
from vpnBot.enums import TransactionCommentEnum
from vpnBot.enums.operation_type_enum import OperationTypeEnum
from vpnBot.exceptions import *
from vpnBot.keyboards.keyboards import get_back_to_main_menu_keyboard
from vpnBot.static.common import DEVICES_MAX_AMOUNT, PRICE
from vpnBot.static.texts_storage import TextsStorage


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


async def add_device_and_check_error(call: types.CallbackQuery) -> Client | None:
    try:
        client = await db_manager.add_client(call.from_user.id)
        return client
    except DevicesLimitError:
        error_text = TextsStorage.ADD_DEVICE_CONFIRMATION_INFO
    except NoAvailableIpsError:
        error_text = TextsStorage.NO_AVAILABLE_IPS_ERROR_MSG
    except NotEnoughMoneyError:
        error_text = TextsStorage.NOT_ENOUGH_MONEY_ERROR_MSG
    except Exception as e:
        print(e)
        error_text = TextsStorage.SOMETHING_WENT_WRONG_ERROR_MSG

    await call.message.answer(
        text=error_text, reply_markup=get_back_to_main_menu_keyboard()
    )
    return None
