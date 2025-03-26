from cybernexvpn.cybernexvpn_bot import config
from cybernexvpn.cybernexvpn_bot.bot import models
from cybernexvpn.cybernexvpn_bot.bot.keyboards.keyboards import get_main_menu_keyboard, get_back_to_main_menu_keyboard, \
     get_fill_up_balance_keyboard
from cybernexvpn.cybernexvpn_bot.bot.models.subscription_updates import UserSubscriptionUpdates

cybernexvpn.cybernexvpn_bot.bot.main import bot
from cybernexvpn.cybernexvpn_bot.bot.models import SubscriptionUpdates
from cybernexvpn.cybernexvpn_bot.bot.utils import new_text_storage
from cybernexvpn.cybernexvpn_bot.bot.utils.client_utils.users import get_users
from cybernexvpn.cybernexvpn_bot.bot.utils.common import send_safely, get_payment_from_redis, delete_payment_from_redis


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


async def handle_payment_succeeded_util(payment_id: str):
    payment = get_payment_from_redis(payment_id)
    if not payment:
        return
    await bot.edit_message_text(
        chat_id=payment.user_id,
        message_id=payment.message_id,
        text=new_text_storage.PAYMENT_SUCCESSFULLY_PROCESSED.format(payment.value),
        parse_mode="HTML",
    )
    await bot.send_message(
        chat_id=payment.user_id,
        text=new_text_storage.MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )
    delete_payment_from_redis(payment_id)

'''
class UserSubscriptionUpdates(BaseModel):
    user: int
    renewed: list[str]
    stopped_due_to_lack_of_funds: list[str]
    stopped_due_to_offed_auto_renew: list[str]
    deleted: list[str]


class SubscriptionUpdates(BaseModel):
    is_reminder: bool
    updates: list[UserSubscriptionUpdates]

'''


def get_reminder_text(renewed, stopped_due_to_lack_of_funds):
    reminder_text = (
        "🔔 Напоминание о продлении подписки\n\n"
        "Завтра день продления подписки для следующих устройств: {}\n."
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


def send_balance_update_notification(user_updates: UserSubscriptionUpdates):
    if user_updates.renewed:


async def make_subscription_updates_util(updates: models.SubscriptionUpdates):

    for user_updates in updates.updates:
        if not (user_updates.renewed or user_updates.stopped_due_to_lack_of_funds):
            continue

        if updates.is_reminder:
            text = get_reminder_text(user_updates.renewed, user_updates.stopped_due_to_lack_of_funds)
        else:
            send_balance_update_notification(user_updates)
            text = get_information_text(user_updates.renewed, user_updates.stopped_due_to_lack_of_funds)

        keyboard = get_fill_up_balance_keyboard() \
            if user_updates.stopped_due_to_lack_of_funds\
            else get_back_to_main_menu_keyboard(with_new_message=True)

        await send_safely(user_updates.user, text, reply_markup=keyboard)
