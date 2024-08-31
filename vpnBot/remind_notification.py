from datetime import datetime

from vpnBot.consts.common import PRICE
from vpnBot.db import db_manager
from vpnBot.db.tables import Client, User
from vpnBot.enums import DayEnum
from vpnBot.utils.date_util import get_next_date


async def send_remind_notifications():
    today = datetime.today().date()
    tomorrow = get_next_date(months_delta=0, days_delta=1)
    day_after_tomorrow = get_next_date(months_delta=0, days_delta=2)
    await send_reminder(today, DayEnum.TODAY)
    await send_reminder(tomorrow, DayEnum.TOMORROW)
    await send_reminder(day_after_tomorrow, DayEnum.DAY_AFTER_TOMORROW)


async def send_reminder(date: datetime.date, day: DayEnum):
    user_to_clients: dict[User, list[Client]] = await db_manager.get_users_clients_by_end_date(date)
    for user, clients in user_to_clients.items():
        payment_sum = len(clients) * PRICE
        if user.balance >= payment_sum:
            return

