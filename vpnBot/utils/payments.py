import time
import logging

from yookassa.domain.notification import WebhookNotification

from cybernexvpn_bot.bot import bot
from vpnBot.consts.texts_storage import TextsStorage
from vpnBot.db import db_manager
from vpnBot.db.tables import Payment
from vpnBot.enums import OperationTypeEnum, TransactionCommentEnum, PaymentStatusEnum
from vpnBot.keyboards.keyboards import get_back_to_main_menu_keyboard

logger = logging.getLogger()


async def update(db_payment: Payment) -> bool:
    return await db_manager.update_balance(
        user_id=db_payment.user_id,
        value=db_payment.value,
        op_type=OperationTypeEnum.INCREASE,
        comment=TransactionCommentEnum.FILL_UP_BALANCE,
    )


async def fill_up_balance(json_payment):
    payment = WebhookNotification(json_payment).object
    db_payment: Payment = await db_manager.get_record(Payment, id=payment.id)

    updated = await update(db_payment)
    if not updated:
        logger.error(f"Error filling balance for user {db_payment.user_id} for {db_payment.value}, trying again.")
        await bot.edit_message_text(
            chat_id=db_payment.user_id,
            message_id=db_payment.related_message_id,
            text=TextsStorage.SOMETHING_WENT_WRONG_TRYING_AGAIN_MSG,
        )
        time.sleep(5)
        updated = await update(db_payment)

    try:
        if updated:
            logger.info(f"User {db_payment.user_id} successfully fill balance for {db_payment.value}.")
            await db_manager.update_payment_status(
                payment.id, PaymentStatusEnum.SUCCEEDED
            )
        else:
            logger.error(f"Error filling balance for user {db_payment.user_id} for {db_payment.value}.")
            await db_manager.update_payment_status(
                payment.id, PaymentStatusEnum.CANCELED
            )
    except Exception:
        pass

    text = (
        TextsStorage.BALANCE_SUCCESSFULLY_FILLED_UP
        if updated
        else TextsStorage.SOMETHING_WENT_VERY_WRONG_ERROR_MSG
    )
    try:
        await bot.edit_message_text(
            chat_id=db_payment.user_id,
            message_id=db_payment.related_message_id,
            text=text,
            reply_markup=get_back_to_main_menu_keyboard(),
        )
    except Exception:
        await bot.send_message(
            chat_id=db_payment.user_id,
            text=text,
            reply_markup=get_back_to_main_menu_keyboard(),
        )
