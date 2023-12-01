from files import Files
from shared import bot
from shared import botDB
from constants import *


# users = botDB.get_all_users()

def send_msg_safety(user_id, text):
    try:
        bot.bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        Files.write_to_logs(f"User {user_id} blocked bot")


users = [MY_ID]
for user in users:
    send_msg_safety(user, 'Короче я потестил, как работает списания и продление подписки, все ок, '
                          'так что теперь номинальная стоимость подписки - 100 рублей в месяц и списания соответственно тоже раз в месяц. '
                          'Дату следующего списания лапками всем перенес ровно на месяц.')
