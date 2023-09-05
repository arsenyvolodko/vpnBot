import os
import time

import pytz
import schedule

from Exceptions.NotEnoughMoneyError import NotEnoughMoneyError
from Ips import Ips
from dispatcher import bot
# from system.main import botDB
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from aiogram import types
from Client import Client
from Keys import Keys
from constants import *
from files import Files
from keyboards import *
from aiogram.types import InputFile


@bot.message_handler(commands="start")
async def start(message: types.Message):
    sent_message = await message.bot.send_message(message.from_user.id, MAIN_MENU_TEXT,
                                                  reply_markup=get_main_menu_keyboard())

    if not botDB.user_exists(message.from_user.id):
        botDB.add_user(message.from_user.id)
        botDB.add_transaction(message.from_user.id, 1, PRICE, sent_message.date.strftime("%Y-%m-%d %H:%M"),
                              'Стартовый баланс')

@bot.message_handler(commands="devices")
async def devices(message: types.Message):
    botDB.get_user_devices(message.from_user.id)
    await check_payment_day()


def check_devices_num(user_id: int):
    devices = botDB.get_user_devices(user_id)
    if len(devices) == 3:
        return False
    devices_nums = [i[0] for i in devices]
    new_device_num = 1 if len(devices) == 0 else max(devices_nums) + 1
    return new_device_num


def get_next_date(date_string: str = None, months: int = 1):
    date = datetime.strptime(date_string, "%Y-%m-%d")
    delta = relativedelta(months=months)
    next_payment_date = date.replace(day=date.day) + delta
    return next_payment_date.strftime("%Y-%m-%d")


def transform_date_string_format(date_string: str, time=False):
    if time:
        date = datetime.strptime(date_string, "%Y-%m-%d %H:%M")
        date = date.strftime("%d.%m.%Y %H:%M")
    else:
        date = datetime.strptime(date_string, "%Y-%m-%d")
        date = date.strftime("%d.%m.%Y")
    return date


async def send_config_and_qr(call: types.CallbackQuery, config_file_path: str, qr_code_file_path: str):
    with open(config_file_path, 'rb') as config_file:
        doc1 = await call.bot.send_document(chat_id=call.from_user.id,
                                            document=InputFile(config_file, filename='NexVpn.conf'))
    doc2 = await call.bot.send_photo(call.from_user.id, open(f'{qr_code_file_path}', 'rb'))
    if doc1 and doc2:
        delete_tmp_client_file(config_file_path)
        delete_tmp_client_file(qr_code_file_path)


def delete_tmp_client_file(file_name: str):
    try:
        os.remove(f'client_files/{file_name}')
    except Exception as e:
        print(f"Cannot delete file {file_name}. Error: {e}")
        return


def process_transaction(transaction: tuple):
    time = transform_date_string_format(transaction[2], time=True)
    text = f'{time}\n'
    text += 'Операция: '
    text += 'списание ' if transaction[0] == 0 else 'пополнение '
    text += str(transaction[1]) + '₽\n'
    text += f'Комментарий: {transaction[3]}'
    return text


def get_user_payments_history(user_id: int):
    balance = botDB.get_balance(user_id)
    text = f'Текущий баланс: {balance}₽\n\n'  # todo добавить строку актуально на момент
    result = botDB.get_transactions(user_id)
    for transaction in result:
        cur_transaction = process_transaction(transaction)
        text += cur_transaction + '\n\n'

    data_file_path = f'client_files/{user_id}_data.txt'
    with open(data_file_path, 'w', encoding='utf-8') as file:
        file.write(text)
        file.close()

    return data_file_path


def update_clients_end_date(user_id, extend_devices: list):
    cur_date = datetime.now().date().strftime("%Y-%m-%d")
    new_date = get_next_date(cur_date)
    for device_num in extend_devices:
        botDB.update_client_end_date(user_id, device_num, new_date)

def deactivate_devices(user_id: int, devices: list):
    for device_num in devices:
        botDB.change_client_activity(user_id, device_num, 0)
        client = botDB.get_client(user_id, device_num)
        Files.remove_client(client)
        print("deactive_client:", client)
        time.sleep(1)


def get_info_subscription_message(cost: float, extend_devices: list, turn_off_devices: list):
    text_to_send = ''
    if len(extend_devices):
        text_for_extended_devices = ''
        for i in extend_devices:
            text_for_extended_devices += f"\"Устройство №{i}\", "
        text_for_extended_devices = text_for_extended_devices[:-2]
        text_to_send = f"С вашего счета списано {cost}₽. \n\n" \
                       f"Подписка для следующих устройств продлена на месяц: {text_for_extended_devices}.\n\n"

    text_for_turn_off_devices = ''
    if len(turn_off_devices):
        for i in turn_off_devices:
            text_for_turn_off_devices += f"\"Устройство №{i}\", "
        text_for_turn_off_devices = text_for_turn_off_devices[:-2]

    if len(text_for_turn_off_devices):
        text_to_send += f'Доступ к VPN для следующих устройств отключен из-за нехватки средств на счете для продления подписки: {text_for_turn_off_devices}.\n\n' \
                        'При пополнении счета подписка будет продлена автоматически. Учтите, что, если устройство будет отключено более 2х месяцев, то оно будет удалено автоматически.'

    return text_to_send

async def extend_subscription(user_id: int, extend_devices: list, turn_off_devices: list):
    if not extend_devices:
        text_to_send = get_info_subscription_message(0, extend_devices, turn_off_devices)
        try:
            await bot.bot.send_message(chat_id=user_id, text=text_to_send)
        except Exception as e:
            print(f'cannot send message to user: {user_id}')
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
    # print("text_to_send: ", text_to_send)
    try:
        msg = await bot.bot.send_message(chat_id=user_id, text=text_to_send)
        cur_time = msg.date.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    deactivate_devices(user_id, turn_off_devices)
    for i in extend_devices:
        botDB.add_transaction(user_id, 0, PRICE, cur_time, f"Продление прописки: \"Устройство №{i}\"")


async def check_users_balances_for_subscription(user_device_map: dict):
    for user in user_device_map:
        user_devices = user_device_map[user]
        user_balance = botDB.get_balance(user)
        print(f'user: {user}, balance: {user_balance}')
        devices_amount = int(user_balance // PRICE)
        extend_devices = user_devices[:devices_amount]
        turn_off_devices = []
        if devices_amount < len(user_devices):
            turn_off_devices = user_devices[devices_amount:]
        print(user_balance, extend_devices, turn_off_devices)
        await extend_subscription(user, extend_devices, turn_off_devices)


async def delete_clients_by_end_date(clients_to_delete):
    for i in clients_to_delete:
        user_id, device_num = i
        ip = Ips(botDB.get_client_ip(user_id, device_num))
        botDB.remove_client_from_db(user_id, device_num)
        added = botDB.add_free_ips(ip)
        print(added)
        await bot.bot.send_message(chat_id=user_id, text=f"Устройство №{device_num} удалено, поскольку было неактивно в течение 2х месяцев")


async def check_payment_day():
    cur_date = datetime.now().date().strftime("%Y-%m-%d")
    clients_to_pay = botDB.get_clients_to_pay(cur_date)
    clients_to_delete = botDB.get_clients_to_delete(get_next_date(cur_date, -2))
    print("clients to delete: ", clients_to_delete)
    await delete_clients_by_end_date(clients_to_delete)  # todo check if works
    if len(clients_to_pay) == 0:
        print("no clients to pay")
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


@bot.callback_query_handler()
async def callback_inline(call: types.CallbackQuery):
    if call.data == BACK_TO_MAIN_MENU_CALLBACK:
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=MAIN_MENU_TEXT,
                                         reply_markup=get_main_menu_keyboard())

    if call.data == DEVICES_CALLBACK:
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="Выберите устройство:",
                                         reply_markup=get_devices_keyboard(call.from_user.id))

    if call.data == ADD_DEVICE_CALLBACK:
        new_device_num = check_devices_num(call.from_user.id)

        if new_device_num is False:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text="К сожалению, Вы можете добавить не более 3х устройств.",
                                             reply_markup=get_back_to_previous_menu(DEVICES_CALLBACK))
            return

        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="После добавления устройства с вашего счета автоматически спишется сумма, "
                                              f"соответсвующая стоимости подписки в месяц за одно устройство - {PRICE}₽.\n"
                                              "Убедитесь, что на вашем счете достаточно средств.",
                                         reply_markup=get_add_device_confirmation_keyboard())

    if call.data == ADD_DEVICE_CONFIRMED_CALLBACK:

        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        new_message = await call.bot.send_message(chat_id=call.from_user.id,
                                                  text="Проверяем данные. Это займет несколько секунд.")
        # try:
        new_device_num = check_devices_num(call.from_user.id)

        if new_device_num is False:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                             text="К сожалению, Вы можете добавить не более 3х устройств.",
                                             reply_markup=get_back_to_previous_menu(DEVICES_CALLBACK))
            return

        balance = botDB.get_balance(call.from_user.id)
        if balance < PRICE:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                             text="На вашем счете недостаточно средств для подключения нового устройства. "
                                                  "Стоимость подписки списывается автоматически после добавления устройства.\n"
                                                  f"Стоимость подписки: {PRICE}₽ в месяц.\n"
                                                  f"На вашем счете: {balance}₽.",
                                             reply_markup=get_not_enough_money_keyboard())
            return

        cur_time = new_message.date.strftime("%Y-%m-%d %H:%M")

        new_balance = balance - PRICE

        try:
            botDB.update_balance(call.from_user.id, new_balance)
        except NotEnoughMoneyError as e:
            call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                       text=SOMETHING_WENT_WRONG_TEXT, reply_markup=get_back_to_main_menu_keyboard())
            return

        botDB.add_transaction(call.from_user.id, 0, PRICE, cur_time, f"Добавлено Устройство №{new_device_num}")

        next_date = get_next_date(new_message.date.strftime("%Y-%m-%d"))

        keys = Keys()
        ips = botDB.get_next_free_ips()

        client = Client(call.from_user.id, new_device_num, ips, keys, next_date)
        botDB.add_client_to_db(client)
        config_file_path, qr_code_file_path = Files.create_client_config_file(client)

        await send_config_and_qr(call, config_file_path, qr_code_file_path)

        await call.bot.delete_message(call.from_user.id, new_message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f"\"Устройство №{new_device_num}\" успешно добавлено. С вашего счета списано {PRICE}₽. "
                                         f"Следующее списание будет произведено автоматически {transform_date_string_format(next_date)}.\n"
                                         f"В случае недостатка средств подписка будет приостановлена и доступ к vpn ограничен.",
                                    reply_markup=get_back_to_main_menu_keyboard())

        Files.update_server_config_file(client)
    # except Exception as e:
        await call.bot.send_message(chat_id=call.from_user.id, text=SOMETHING_WENT_WRONG_TEXT,
                                    reply_markup=get_back_to_main_menu_keyboard())
        # raise e
        # print(f"Cannot add device for user: {call.from_user.id}.\n Error: {e}")
          

    if 'specific_device_callback#' in call.data:
        device_num = int(re.sub('specific_device_callback#', '', call.data))
        active = botDB.check_if_active(call.from_user.id, device_num)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"Устройство №{device_num}:",
                                         reply_markup=get_specific_device_keyboard(bool(active)))

    if call.data == GET_QR_AND_CONFIG_CALLBACK:
        device_num = int(re.sub('Устройство №', '', call.message.text)[:-1])
        client = botDB.get_client(call.from_user.id, device_num)
        config_file_path, qr_code_file_path = Files.create_client_config_file(client)
        await call.bot.delete_message(call.from_user.id, call.message.message_id)
        await send_config_and_qr(call, config_file_path, qr_code_file_path)
        await call.bot.send_message(call.from_user.id, MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())

    if call.data == DELETE_DEVICE_CALLBACK:
        device_num = int(re.search('[0-9]+', call.message.text).group())
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="После удаления устройства доступ к VPN с этого устройства будет ограничен. "
                                              f"Вы уверены, что хотите удалить \"Устройство №{device_num}\"?",
                                         reply_markup=get_delete_device_confirmation_keyboard())

    if call.data == DELETE_DEVICE_CONFIRM_CALLBACK:
        device_num = int(re.search('[0-9]+', call.message.text).group())
        client = botDB.get_client(call.from_user.id, device_num)
        removed_from_server_config = Files.remove_client(client)
        removed_from_db = botDB.remove_client_from_db(client.user_id, client.device_num)

        if not removed_from_db or not removed_from_server_config:
            call.bot.edit_message_text(call.from_user.id, call.message.message_id,
                                       SOMETHING_WENT_WRONG_TEXT, get_back_to_main_menu_keyboard())
            return

        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f'\"Устройство №{device_num}\" успешно удалено',
                                         reply_markup=get_back_to_main_menu_keyboard())

        botDB.add_free_ips(client.ips)


    if call.data == EXTEND_SUBSCRIPTION_FOR_DEVICE_CALLBACK:
        device_num = int(re.search('[0-9]+', call.message.text).group())
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                   text=f"Устройство №{device_num}:\n"
                                        f"После продления подписки для данного устройства с вашего счета спишется сумма, "
                                        f"соответсвующая стоимости подписки в месяц - {PRICE}₽.\n"
                                        f"Убедитесь, что на вашем счете достаточно средств.",
                                   reply_markup=get_extend_subscription_confirmation_keyboard())

    if call.data == EXTEND_SUBSCRIPTION_FOR_DEVICE_CONFIRM_CALLBACK:
        device_num = int(re.search('[0-9]+', call.message.text).group())
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        new_message = await call.bot.send_message(chat_id=call.from_user.id,  # todo вот если тут не отправится - все ебнется, а не хотелось бы
                                                  text="Проверяем данные. Это займет несколько секунд.")

        balance = botDB.get_balance(call.from_user.id)
        if balance < PRICE:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                             text="На вашем счете недостаточно средств для продления подписки."
                                                  f"Стоимость подписки: {PRICE}₽ в месяц.\n"
                                                  f"На вашем счете: {balance}₽.",
                                             reply_markup=get_not_enough_money_keyboard())
            return

        cur_time = new_message.date.strftime("%Y-%m-%d %H:%M")

        new_balance = balance - PRICE

        try:
            botDB.update_balance(call.from_user.id, new_balance)
        except NotEnoughMoneyError as e:
            call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                       text=SOMETHING_WENT_WRONG_TEXT, reply_markup=get_back_to_main_menu_keyboard())
            return

        botDB.add_transaction(call.from_user.id, 0, PRICE, cur_time, f"Продление прописки: \"Устройство №{device_num}\"")

        next_date = get_next_date(new_message.date.strftime("%Y-%m-%d"))

        botDB.change_client_activity(call.from_user.id, device_num, 1)
        botDB.update_client_end_date(call.from_user.id, device_num, next_date)
        client = botDB.get_client(call.from_user.id, device_num)

        await call.bot.delete_message(call.from_user.id, new_message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f"Подписка для устройства №{device_num} успешно продлена.\nС вашего счета списано {PRICE}₽. "
                                         f"Следующее списание будет произведено автоматически {transform_date_string_format(next_date)}.\n"
                                         f"В случае недостатка средств подписка будет приостановлена и доступ к vpn ограничен.",
                                    reply_markup=get_back_to_main_menu_keyboard())

        Files.update_server_config_file(client)

        print(device_num)


    ### finance

    if call.data == FINANCE_CALLBACK:
        balance = botDB.get_balance(call.from_user.id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"На Вашем счете: {balance}₽", reply_markup=get_finance_keyboard())

    if call.data == PAYMENTS_HISTORY_CALLBACK:
        user_data_file_path = get_user_payments_history(call.from_user.id)
        # await call.bot.send_document(call.from_user.id, ('balance history.txt', user_data_file_path))
        with open(user_data_file_path, 'rb') as file:
            await call.bot.send_document(chat_id=call.from_user.id, document=InputFile(file,
                                                                                       filename='balance history.txt'))  # todo добавить какой-нибудь текст
        await call.bot.delete_message(call.from_user.id, call.message.message_id)
        await call.bot.send_message(call.from_user.id, MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())

    if call.data == FILL_UP_CALLBACK:
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="Выберите сумму", reply_markup=get_fill_up_balance_keyboard())

    if call.data in FILL_UP_BALANCE_CALLBACKS_MAP:
        sum_value = FILL_UP_BALANCE_CALLBACKS_MAP[call.data]
        sent_message = await call.bot.send_message(chat_id=call.from_user.id, text="ок")
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=sent_message.message_id)
        balance = botDB.get_balance(call.from_user.id)
        new_balance = balance + sum_value
        balance_updated = botDB.update_balance(call.from_user.id, new_balance)
        if balance_updated:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                      text=f"Ваш баланс успешно пополнен на {sum_value}₽", reply_markup=get_back_to_main_menu_keyboard())

            botDB.add_transaction(call.from_user.id, 1, sum_value, sent_message.date.strftime("%Y-%m-%d %H:%M"),
                                  'Пополнение баланса')
        else:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text=SOMETHING_WENT_WRONG_TEXT, reply_markup=get_back_to_main_menu_keyboard())