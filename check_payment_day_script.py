import asyncio
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from shared import bot, botDB
from Ips import Ips
from constants import PRICE
from files import Files
from constants import *


def get_next_date(date_string: str = None, months: int = 1):
    date = datetime.strptime(date_string, "%Y-%m-%d")
    delta = relativedelta(months=months)
    next_payment_date = date.replace(day=date.day) + delta
    return next_payment_date.strftime("%Y-%m-%d")


def update_clients_end_date(user_id, extend_devices: list):
    cur_date = datetime.now().date().strftime("%Y-%m-%d")
    new_date = get_next_date(cur_date)
    for device_num in extend_devices:
        botDB.update_client_end_date(user_id, device_num, new_date)
        logs.write(f'{cur_date}: subscription extended for device {device_num} of user {user_id}')


def deactivate_devices(user_id: int, devices: list):
    for device_num in devices:
        botDB.change_client_activity(user_id, device_num, 0)
        client = botDB.get_client(user_id, device_num)
        Files.remove_client(client)
        cur_date = datetime.now().date().strftime("%Y-%m-%d")
        logs.write(f'{cur_date}: deactivate device: {device_num} for user {user_id}\n')
        time.sleep(1)


def get_info_subscription_message(cost: int, extend_devices: list, turn_off_devices: list):
    text_to_send = ''
    if len(extend_devices):
        text_for_extended_devices = ''
        for i in extend_devices:
            text_for_extended_devices += f"\"Устройство №{i}\", "
        text_for_extended_devices = text_for_extended_devices[:-2]
        text_to_send = f"С вашего счета списано {cost}₽. \n" \
                       f"Подписка для следующих устройств продлена на месяц: {text_for_extended_devices}.\n\n"

    text_for_turn_off_devices = ''
    if len(turn_off_devices):
        for i in turn_off_devices:
            text_for_turn_off_devices += f"\"Устройство №{i}\", "
        text_for_turn_off_devices = text_for_turn_off_devices[:-2]

    if len(text_for_turn_off_devices):
        text_to_send += (
            f'Доступ к VPN для следующих устройств: {text_for_turn_off_devices} приостановлен из-за нехватки '
            f'средств на счете.\n'
            'Для продления подписки пополните баланс, перейдите в раздел \"Устройства\", выберите соответсвующее '
            'устройство и нажмите \"Продлить подписку\".\nУчтите, что, если устройство будет отключено более 2х '
            'месяцев, то оно будет удалено автоматически.')

    return text_to_send


async def extend_subscription(user_id: int, extend_devices: list, turn_off_devices: list):
    if not extend_devices:
        text_to_send = get_info_subscription_message(0, extend_devices, turn_off_devices)
        try:
            await bot.bot.send_message(chat_id=user_id, text=text_to_send)
        except Exception:
            pass
        deactivate_devices(user_id, turn_off_devices)
        return
    user_balance = botDB.get_balance(user_id)
    cost = len(extend_devices) * PRICE
    new_balance = user_balance - cost
    if new_balance < 0:
        await check_users_balances_for_subscription({user_id: extend_devices + turn_off_devices})
        return
    botDB.update_balance(user_id, new_balance)
    update_clients_end_date(user_id, extend_devices)
    text_to_send = get_info_subscription_message(cost, extend_devices, turn_off_devices)
    try:
        msg = await bot.bot.send_message(chat_id=user_id, text=text_to_send)
        cur_time = msg.date.strftime("%Y-%m-%d %H:%M")
    except Exception:
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    deactivate_devices(user_id, turn_off_devices)
    for i in extend_devices:
        botDB.add_transaction(user_id, 0, PRICE, cur_time, f"Продление прописки: \"Устройство №{i}\"")


async def check_users_balances_for_subscription(user_device_map: dict):
    for user in user_device_map:
        user_devices = user_device_map[user]
        user_balance = botDB.get_balance(user)
        devices_amount = int(user_balance // PRICE)
        extend_devices = user_devices[:devices_amount]
        turn_off_devices = []
        if devices_amount < len(user_devices):
            turn_off_devices = user_devices[devices_amount:]
        await extend_subscription(user, extend_devices, turn_off_devices)


async def delete_clients_by_end_date(clients_to_delete, cur_date):
    for i in clients_to_delete:
        user_id, device_num = i
        ip = Ips(botDB.get_client_ip(user_id, device_num))
        botDB.remove_client_from_db(user_id, device_num)
        botDB.add_free_ips(ip)
        logs.write(f'{cur_date}: delete client {device_num} for user {user_id} after 2 months')
        await bot.bot.send_message(chat_id=user_id,
                                   text=f"Устройство №{device_num} удалено, поскольку было неактивно в течение 2х "
                                        f"месяцев")


async def check_payment_day():
    cur_date = datetime.now().date().strftime("%Y-%m-%d")
    clients_to_pay = botDB.get_clients_to_pay(cur_date)
    clients_to_delete = botDB.get_clients_to_delete(get_next_date(cur_date, -2))
    await delete_clients_by_end_date(clients_to_delete, cur_date)
    if len(clients_to_pay) == 0:
        logs.write(f'{cur_date}: no clients to delete after 2 months')
        return
    user_device_map = {}
    for client in clients_to_pay:
        user_id, device_num = client[0], client[1]
        if user_id not in user_device_map:
            user_device_map[user_id] = [device_num]
        else:
            user_device_map[user_id].append(device_num)
    for user in user_device_map:
        user_device_map[user].sort()

    await check_users_balances_for_subscription(user_device_map)


async def schedule_check_payment_day():
    await check_payment_day()


if __name__ == '__main__':
    logs = open(PATH_TO_LOGS, 'a')
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(schedule_check_payment_day())
        botDB.close()
        loop.close()
    except Exception as e:
        print(e)
    finally:
        logs.close()
