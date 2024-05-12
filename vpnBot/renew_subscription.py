import asyncio
import datetime

from vpnBot.bot.main import bot
from vpnBot.db import db_manager
from vpnBot.exceptions.clients import NotEnoughMoneyError
from vpnBot.static.texts_storage import TextsStorage
from vpnBot.utils.date_util import get_next_date


async def handle_today_payments():
    cur_date = datetime.date.today()
    clients_to_pay_today = await db_manager.get_clients_by_end_date(
        end_date=cur_date, activity_status=True  # todo change to <=
    )
    new_payment_date: datetime.date = get_next_date(start_date=cur_date)

    for client in clients_to_pay_today:
        try:
            result = TextsStorage.SUBSCRIPTION_SUCCESSFULLY_RENEWED
            await db_manager.renew_subscription(
                client.id, client.user_id, new_payment_date
            )
        except NotEnoughMoneyError:
            result = TextsStorage.SUBSCRIPTION_NOT_RENEWED
        except Exception:
            print("beda")
            return

        await bot.send_message(client.user_id, result.format(client.device_num))


async def handle_delete_clients():
    old_payment_date: datetime.date = get_next_date(months_delta=-2)
    clients_to_delete = await db_manager.get_clients_by_end_date(
        end_date=old_payment_date, activity_status=False
    )
    for client in clients_to_delete:
        await db_manager.delete_client(client)
        await bot.send_message(
            chat_id=client.user_id, text=TextsStorage.INACTIVE_DEVICE_DELETED
        )


async def main():
    await handle_today_payments()
    await handle_delete_clients()


if __name__ == "__main__":
    asyncio.run(main())