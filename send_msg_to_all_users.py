from files import Files
from shared import bot
from shared import botDB
import asyncio
from constants import *


async def send_msg_safety(user_id, text):
    try:
        bot.bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        Files.write_to_logs(f"User {user_id} blocked bot")


async def send_msg():
    users = [MY_ID]
    # users = botDB.get_all_users()
    for user in users:
        await send_msg_safety(user, 'Короче я потестил, как работает списания и продление подписки, все ок, '
                                    'так что теперь номинальная стоимость подписки - 100 рублей в месяц и списания соответственно тоже раз в месяц. '
                                    'Дату следующего списания лапками всем перенес ровно на месяц.')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_msg())
    botDB.close()
    loop.close()
