from classes_util.Files import Files
from shared import bot
from shared import botDB
import asyncio


async def send_msg_safety(user_id, text):
    try:
        await bot.bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        Files.write_to_logs(f"User {user_id} blocked bot")


async def send_msg():
    # users = [MY_ID]
    users = botDB.get_all_users()
    for user in users:
        await send_msg_safety(user, 'Всем привет в этом чатике, долгожданный момент настал и сервер сдох,'
                                    ' соответственно и vpn тоже, наша команда специалистов в лице @arseny_volodko и @arseny_volodko '
                                    'когда-нибудь обязательно найдет время (в течение ближайших пары дней) это пофиксить или купить сервер помощнее, '
                                    'а пока что устраиваем детокс от рилсов в инстраграммах')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_msg())
    botDB.close()
    loop.close()
