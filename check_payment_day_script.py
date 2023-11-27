import asyncio
import time
from shared import bot, botDB
from Ips import Ips
from files import Files
from constants import *
from DateFunc import DateFunc


def update_clients_end_date(user_id, extend_devices: list):
    cur_date = DateFunc.get_cur_date()
    new_date = DateFunc.get_next_date(cur_date)
    for device_num in extend_devices:
        botDB.update_client_end_date(user_id, device_num, new_date)
        Files.write_to_logs(f'subscription extended for device {device_num} of user {user_id}'), str(
            __file__.split('/')[-1])


def deactivate_devices(user_id: int, devices: list):
    for device_num in devices:
        botDB.change_client_activity(user_id, device_num, 0)
        client = botDB.get_client(user_id, device_num)
        Files.remove_client(client, False)
        Files.write_to_logs(f'deactivate device: {device_num} for user {user_id} due to lack of funds',
                            str(__file__.split('/')[-1]))
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
        cur_time = DateFunc.get_cur_time()
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


async def delete_clients_by_end_date(clients_to_delete):
    for i in clients_to_delete:
        user_id, device_num = i
        ip = Ips(botDB.get_client_ip(user_id, device_num))
        botDB.remove_client_from_db(user_id, device_num)
        botDB.add_free_ips(ip)
        Files.write_to_logs(f'client {device_num} for user {user_id} deleted after 2 months of inactivity',
                            str(__file__.split('/')[-1]))
        await bot.bot.send_message(chat_id=user_id,
                                   text=f"Устройство №{device_num} удалено, поскольку было неактивно в течение 2х "
                                        f"месяцев")


async def check_payment_day():
    cur_date = DateFunc.get_cur_date()
    clients_to_pay = botDB.get_clients_to_pay(cur_date)
    clients_to_delete = botDB.get_clients_to_delete(DateFunc.get_next_date(cur_date, days=0, months=-2))
    await delete_clients_by_end_date(clients_to_delete)
    if len(clients_to_pay) == 0:
        Files.write_to_logs('no clients to delete', str(__file__.split('/')[-1]))
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
    Files.write_to_logs("started execution every_day_script")
    Files.make_back_up_copy()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(schedule_check_payment_day())
        botDB.close()
        loop.close()
    except Exception as e:
        print(e)
    Files.run_bash_sync_script()
    Files.write_to_logs("ended execution every_day_script")
