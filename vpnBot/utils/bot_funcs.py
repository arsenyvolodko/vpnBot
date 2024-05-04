from aiogram import types

from vpnBot.db.manager import db_manager
from vpnBot.db.tables import User, Transaction
from vpnBot.enums import TransactionCommentEnum


async def add_and_get_user(message: types.Message):
    user = await db_manager.get_user_by_id(message.from_user.id)
    if not user:
        user = await db_manager.add_record(
            User,
            id=message.from_user.id,
            username=message.from_user.username
        )
    await db_manager.add_record(
        Transaction,
        user_id=user.id,
        operation_type=True,
        comment=TransactionCommentEnum.START_BALANCE
    )


async def get_user_balance(user_id: int):
    user = await db_manager.get_user_by_id(user_id)
    return user.balance

