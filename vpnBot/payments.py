from yookassa.domain.notification import WebhookNotification

from vpnBot.bot.main import bot
from vpnBot.consts.texts_storage import TextsStorage
from vpnBot.db import db_manager
from vpnBot.db.tables import Payment
from vpnBot.enums import OperationTypeEnum, TransactionCommentEnum
from vpnBot.keyboards.keyboards import get_back_to_main_menu_keyboard


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
        await bot.edit_message_text(
            chat_id=db_payment.user_id,
            message_id=db_payment.related_message_id,
            text=TextsStorage.SOMETHING_WENT_WRONG_TRYING_AGAIN_MSG,
        )
        updated = await update(db_payment)

    text = (
        TextsStorage.BALANCE_SUCCESSFULLY_FILLED_UP
        if updated
        else TextsStorage.SOMETHING_WENT_VERY_WRONG_ERROR_MSG
    )

    await bot.edit_message_text(
        chat_id=db_payment.user_id,
        message_id=db_payment.related_message_id,
        text=text,
        reply_markup=get_back_to_main_menu_keyboard(),
    )
