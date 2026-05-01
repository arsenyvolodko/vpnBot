import logging

from aiogram.enums import ParseMode

from cybernexvpn.cybernexvpn_bot import config
from cybernexvpn.cybernexvpn_bot.bot import models
from cybernexvpn.cybernexvpn_bot.bot.keyboards.keyboards import get_main_menu_keyboard, get_back_to_main_menu_keyboard, \
    get_fill_up_balance_keyboard, get_devices_reactivate_keyboard, get_web_panel_keyboard
from cybernexvpn.cybernexvpn_bot.bot.models.subscription_updates import UserSubscriptionUpdates

from cybernexvpn.cybernexvpn_bot.bot.main import bot
from cybernexvpn.cybernexvpn_bot.bot.utils import new_text_storage
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.clients import get_user_clients
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.users import get_users
from cybernexvpn.cybernexvpn_bot.bot.utils.common import send_safely, get_payment_from_redis, delete_payment_from_redis, \
    send_and_pin

logger = logging.getLogger(__name__)


async def send_message_from_admin_util(message_schema: models.Message):
    kwargs = {
        "text": message_schema.text,
        "parse_mode": "HTML",
        "reply_markup": get_back_to_main_menu_keyboard(with_new_message=True)
    }

    if message_schema.only_to_me:
        await send_safely(config.ADMIN_USER_ID, **kwargs)
    else:
        users = await get_users()
        if not users:
            return

        for user in users:
            await send_safely(
                user.id,
                **kwargs
            )


async def send_pinned_message_from_admin_util(message_schema: models.PinnedMessage):
    users = await get_users()
    if not users:
        return

    if message_schema.only_to_me:
        users = [user for user in users if user.id == config.ADMIN_USER_ID]

    for user in users:
        await send_and_pin(
            chat_id=user.id,
            text=message_schema.text,
            parse_mode="HTML",
            reply_markup=get_web_panel_keyboard(user.token),
        )


async def handle_payment_succeeded_util(user_id: int, payment_id: str):
    payment = get_payment_from_redis(payment_id)
    delete_payment_from_redis(payment_id)

    if payment:
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=payment.message_id,
            text=new_text_storage.PAYMENT_SUCCESSFULLY_PROCESSED_WITH_VALUE.format(payment.value),
            parse_mode=ParseMode.HTML,
        )
    else:
        await send_safely(
            chat_id=user_id,
            text=new_text_storage.PAYMENT_SUCCESSFULLY_PROCESSED,
        )

    clients = await get_user_clients(user_id, None)

    inactive_clients = [
        client for client in clients if client.is_active is False and clients
    ] if clients else []

    if not inactive_clients:
        await send_safely(
            chat_id=user_id,
            text=new_text_storage.MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
        )
        return

    text = new_text_storage.REACTIVATE_DEVICE_AFTER_FILL_UP \
        if len(inactive_clients) == 1 \
        else new_text_storage.REACTIVATE_DEVICES_AFTER_FILL_UP

    await send_safely(
        chat_id=user_id,
        text=text,
        reply_markup=get_devices_reactivate_keyboard(inactive_clients),
        parse_mode=ParseMode.HTML,
    )


def get_reminder_text(renewed, stopped_due_to_lack_of_funds):
    reminder_text = (
        "🔔 Напоминание о продлении подписки\n\n"
        "Завтра день продления подписки для следующих устройств: {}.\n"
    )
    reminder_text2 = (
        "Не забудь пополнить баланс, иначе подписка будет приостановлена для следующих устройств: {}\n"
    )

    all_clients_to_inform_about = renewed + stopped_due_to_lack_of_funds
    all_clients_str = ", ".join([f"«{client}»" for client in all_clients_to_inform_about])
    clients_to_stop_str = ", ".join([f"«{client}»" for client in stopped_due_to_lack_of_funds])

    text = reminder_text.format(all_clients_str)
    if stopped_due_to_lack_of_funds:
        text += reminder_text2.format(clients_to_stop_str)

    return text


def get_information_text(renewed_clients, stopped_due_to_lack_of_funds):
    information_text = (
        "🔔 Информация о продлении подписки\n\n"
    )

    success_text = "Подписка успешно продлена для следующих устройств: {}\n"
    fail_text = "Подписка приостановлена для следующих устройств из-за нехватки средств: {}\n"

    if renewed_clients:
        renewed_clients_str = ", ".join([f"«{client}»" for client in renewed_clients])
        information_text += success_text.format(renewed_clients_str)

    if stopped_due_to_lack_of_funds:
        stopped_due_to_lack_of_funds_str = ", ".join([f"«{client}»" for client in stopped_due_to_lack_of_funds])
        information_text += fail_text.format(stopped_due_to_lack_of_funds_str)

    return information_text


async def send_balance_update_notification(user_updates: UserSubscriptionUpdates):
    if user_updates.renewed and user_updates.total_price:
        await send_safely(
            user_updates.user,
            text=new_text_storage.FUNDS_DEBITED_SUM.format(user_updates.total_price),
        )


async def make_subscription_updates_util(updates: models.SubscriptionUpdates):

    for user_updates in updates.updates:
        logger.info("sending updates to user: %s", user_updates.user)
        if not (user_updates.renewed or user_updates.stopped_due_to_lack_of_funds):
            continue

        if updates.is_reminder:
            text = get_reminder_text(user_updates.renewed, user_updates.stopped_due_to_lack_of_funds)
        else:
            await send_balance_update_notification(user_updates)
            text = get_information_text(user_updates.renewed, user_updates.stopped_due_to_lack_of_funds)

        keyboard = get_fill_up_balance_keyboard() \
            if user_updates.stopped_due_to_lack_of_funds\
            else get_back_to_main_menu_keyboard(with_new_message=True)

        await send_safely(user_updates.user, text, reply_markup=keyboard)
