import os
import re
from datetime import datetime
from io import BytesIO
from aiogram.types import InputFile

import Exceptions
from DateFunc import DateFunc
from shared import bot, botDB
from Client import Client
from Keys import Keys
from files import Files
from keyboards import *
from constants import *


@bot.message_handler(commands=["start"])
async def welcome_message(message: types.Message):
    sent_message = await message.bot.send_message(message.from_user.id, START_TEXT,
                                                  reply_markup=to_main_menu_keyboard())
    if not botDB.user_exists(message.from_user.id):
        botDB.add_user(message.from_user.username, message.from_user.id)
        botDB.add_transaction(message.from_user.id, 1, PRICE, sent_message.date.strftime("%Y-%m-%d %H:%M"),
                              'Стартовый баланс')
        if message.get_args():
            await handle_new_user_by_link(message)
            Files.write_to_logs(
                f"New user: {message.from_user.username}: {message.from_user.id} invited by {message.get_args()}")
        Files.write_to_logs(f"New user: {message.from_user.username}: {message.from_user.id}")


@bot.message_handler(commands=["menu"])
async def menu_message(message: types.Message):
    if botDB.user_exists(message.from_user.id):
        await message.bot.send_message(message.from_user.id, MAIN_MENU_TEXT,
                                       reply_markup=get_main_menu_keyboard())
        return
    await message.bot.send_message(message.from_user.id,
                                   "Используйте команду /start для того, чтобы начать пользоваться ботом.")


async def handle_new_user_by_link(message: types.Message):
    from_user_id = int(message.get_args())
    res = await fill_up_balance_actions_for_message(message, 50, False, from_user_id)
    if res:
        Files.write_to_logs(f"начислено 50₽ пользователю {from_user_id} за приглашение нового пользователя")
    else:
        await message.bot.send_message(chat_id=from_user_id,
                                       text="Вы успешно пригласили нового пользователя, но произошла какая-то ошибка. Напишите @arseny_volodko.")
        Files.write_to_logs(f"ошибка начисления средств пользователю {from_user_id} за приглашение")


def check_devices_num(user_id: int):
    user_devices = botDB.get_user_devices(user_id)
    if len(user_devices) == 3:
        return False
    devices_nums = [i[0] for i in user_devices]
    new_device_num = 1 if len(user_devices) == 0 else max(devices_nums) + 1
    return new_device_num


def transform_date_string_format(date_string: str, time=False):
    if time:
        date = datetime.strptime(date_string, "%Y-%m-%d %H:%M")
        date = date.strftime("%d.%m.%Y %H:%M")
    else:
        date = datetime.strptime(date_string, "%Y-%m-%d")
        date = date.strftime("%d.%m.%Y")
    return date


async def send_config_and_qr(call: types.CallbackQuery, config_file_path: str, qr_code_file_path: str):
    try:
        with open(config_file_path, 'rb') as config_file:
            file_data = BytesIO(config_file.read())
            doc1 = await call.bot.send_document(chat_id=call.from_user.id,
                                                document=InputFile(file_data, filename='NexVpn.conf'))
        doc2 = await call.bot.send_photo(call.from_user.id, open(f'{qr_code_file_path}', 'rb'))
        if doc1 and doc2:
            delete_tmp_client_file(config_file_path)
            delete_tmp_client_file(qr_code_file_path)
            return True
    except Exception:
        return False


def delete_tmp_client_file(file_name: str):
    try:
        os.remove(f'{file_name}')
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
    cur_time = DateFunc.get_cur_time()
    text = f'Текущий баланс: {balance}₽\n\n'
    result = botDB.get_transactions(user_id)
    for transaction in result:
        cur_transaction = process_transaction(transaction)
        text += cur_transaction + '\n\n'

    text += f"Актуально на момент: {cur_time}."

    data_file_path = f'{PATH_TO_CLIENTS_FILES}/{user_id}_data.txt'
    with open(data_file_path, 'w', encoding='utf-8') as file:
        file.write(text)
        file.close()

    return data_file_path


@bot.callback_query_handler()
async def callback_inline(call: types.CallbackQuery):
    if call.data == BACK_TO_MAIN_MENU_CALLBACK:
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=MAIN_MENU_TEXT,
                                         reply_markup=get_main_menu_keyboard())

    elif call.data == DEVICES_CALLBACK:
        curr_devices = botDB.get_user_devices(call.from_user.id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="Выберите устройство:",
                                         reply_markup=get_devices_keyboard(curr_devices))

    elif call.data == ADD_DEVICE_CALLBACK:
        new_device_num = check_devices_num(call.from_user.id)

        if new_device_num is False:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text="К сожалению, Вы можете добавить не более 3х устройств.",
                                             reply_markup=get_back_to_previous_menu(DEVICES_CALLBACK))
            return

        user_balance = botDB.get_balance(call.from_user.id)

        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="После добавления устройства с вашего счета автоматически спишется сумма, "
                                              f"соответсвующая стоимости подписки в сутки за одно устройство - {PRICE}₽.\n"  # todo в месяц
                                              f"На Вашем счете - {user_balance}₽.",
                                         reply_markup=get_add_device_confirmation_keyboard())

    elif call.data == ADD_DEVICE_CONFIRMED_CALLBACK:

        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        new_message = await call.bot.send_message(chat_id=call.from_user.id,
                                                  text="Проверяем данные. Это займет несколько секунд.")

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
                                                  f"Стоимость подписки: {PRICE}₽ в сутки.\n"  # todo в месяц
                                                  f"На вашем счете: {balance}₽.",
                                             reply_markup=get_not_enough_money_keyboard())
            return

        cur_time = new_message.date.strftime("%Y-%m-%d %H:%M")
        new_balance = balance - PRICE

        next_date = DateFunc.get_next_date(new_message.date.strftime("%Y-%m-%d"))

        keys = Keys()
        try:
            ips = botDB.get_next_free_ips()
        except Exceptions.NoFreeIPsError:
            await call.bot.send_message(chat_id=MY_ID,
                                        text=f"No more free IPs available, user: @{call.from_user.username}")
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                             text="Вам удивительно повезло стать тем человеком, на котором на сервере закончились "
                                                  "свободные IP адреса. Мы уже работаем над устранением проблемы, приносим извинения "
                                                  "за то, что не оправдали Ваших ожиданий. Мы напишем Вам, когда исправим проблему и "
                                                  "предоставим 3 месяца подписки бесплатно.\nЕсли вы уже пополнили свой баланс, но хотите "
                                                  "вывести средства обратно, напишите @arseny_volodko.")

            Files.write_to_logs("no more free IPs available, user: @{call.from_user.username}")
            return

        client = Client(call.from_user.id, new_device_num, ips, keys, next_date)
        botDB.add_client_to_db(client)
        config_file_path, qr_code_file_path = Files.create_client_config_file(client)
        updated = Files.update_server_config_file(client)
        if updated:
            sent = await send_config_and_qr(call, config_file_path, qr_code_file_path)
        else:
            sent = False

        if not (updated and sent):
            try:
                await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                                 text=SOMETHING_WENT_WRONG_TEXT,
                                                 reply_markup=get_back_to_main_menu_keyboard())
                botDB.remove_client_from_db(client.user_id, client.device_num)
                botDB.add_free_ips(ips)
                Files.remove_client(client)
            except Exception:
                pass
            return

        botDB.update_balance(call.from_user.id, new_balance)
        botDB.add_transaction(call.from_user.id, 0, PRICE, cur_time, f"Добавлено Устройство №{new_device_num}")

        await call.bot.delete_message(call.from_user.id, new_message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f"\"Устройство №{new_device_num}\" успешно добавлено. С вашего счета списано {PRICE}₽. "
                                         f"Следующее списание будет произведено автоматически {transform_date_string_format(next_date)}.\n"
                                         f"В случае недостатка средств подписка будет приостановлена и доступ к vpn ограничен.",
                                    reply_markup=get_back_to_main_menu_keyboard())

        Files.write_to_logs(f"user {client.user_id} added device {client.device_num}")

    elif 'specific_device_callback#' in call.data:
        device_num = int(re.sub('specific_device_callback#', '', call.data))
        active = botDB.check_if_active(call.from_user.id, device_num)
        if active:
            status = 'активно'
            sub_info = f"Следующее списание: {transform_date_string_format(botDB.get_client_end_date(call.from_user.id, device_num))}."
        else:
            status = 'неактивно'
            sub_info = f'Если не продлить подписку до {DateFunc.get_next_date(botDB.get_client_end_date(call.from_user.id, device_num), days=0, months=2)}, то устройство будет удалено.'
        device_info_text = (f"Устройство №{device_num}.\n"
                            f"Cтатус: {status}.\n"
                            f"{sub_info}")
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=device_info_text,
                                         reply_markup=get_specific_device_keyboard(bool(active)))

    elif call.data == GET_QR_AND_CONFIG_CALLBACK:
        # device_num = int(re.sub('Устройство №', '', call.message.text)[:-1])
        device_num = int(re.search('[0-9]+', call.message.text).group())
        client = botDB.get_client(call.from_user.id, device_num)
        config_file_path, qr_code_file_path = Files.create_client_config_file(client)
        await call.bot.delete_message(call.from_user.id, call.message.message_id)
        await send_config_and_qr(call, config_file_path, qr_code_file_path)
        await call.bot.send_message(call.from_user.id, MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())

    elif call.data == DELETE_DEVICE_CALLBACK:
        device_num = int(re.search('[0-9]+', call.message.text).group())
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="После удаления устройства доступ к VPN с этого устройства будет ограничен. "
                                              f"Вы уверены, что хотите удалить \"Устройство №{device_num}\"?",
                                         reply_markup=get_delete_device_confirmation_keyboard())

    elif call.data == DELETE_DEVICE_CONFIRM_CALLBACK:
        device_num = int(re.search('[0-9]+', call.message.text).group())
        client = botDB.get_client(call.from_user.id, device_num)
        removed_from_server_config = Files.remove_client(client)
        removed_from_db = botDB.remove_client_from_db(client.user_id, client.device_num)

        if not (removed_from_db and removed_from_server_config):
            call.bot.edit_message_text(call.from_user.id, call.message.message_id,
                                       SOMETHING_WENT_WRONG_TEXT, get_back_to_main_menu_keyboard())
            return

        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f'\"Устройство №{device_num}\" успешно удалено',
                                         reply_markup=get_back_to_main_menu_keyboard())
        Files.write_to_logs(f"user {call.from_user.id} removed device number {client.device_num}.")
        res = botDB.add_free_ips(client.ips)
        if res:
            Files.write_to_logs(f"successfully added ips to db: {client.ips.get_ipv4()}")
        else:
            Files.write_to_logs(f"failed to add ips to db: {client.ips.get_ipv4()}")

    elif call.data == EXTEND_SUBSCRIPTION_FOR_DEVICE_CALLBACK:
        device_num = int(re.search('[0-9]+', call.message.text).group())
        user_balance = botDB.get_balance(call.from_user.id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"Устройство №{device_num}:\n"
                                              f"После продления подписки для данного устройства с вашего счета спишется сумма, "
                                              f"соответсвующая стоимости подписки в сукти - {PRICE}₽.\n"  # todo в месяц
                                              f"На Вашем счете - {user_balance}₽.",
                                         reply_markup=get_extend_subscription_confirmation_keyboard())

    elif call.data == EXTEND_SUBSCRIPTION_FOR_DEVICE_CONFIRM_CALLBACK:
        device_num = int(re.search('[0-9]+', call.message.text).group())
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        new_message = await call.bot.send_message(chat_id=call.from_user.id,
                                                  # todo вот если тут не отправится - все ебнется, а не хотелось бы
                                                  text="Проверяем данные. Это займет несколько секунд.")

        balance = botDB.get_balance(call.from_user.id)
        if balance < PRICE:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                             text="На вашем счете недостаточно средств для продления подписки."
                                                  f"Стоимость подписки: {PRICE}₽ в сутки.\n"  # todo в месяц
                                                  f"На вашем счете: {balance}₽.",
                                             reply_markup=get_not_enough_money_keyboard())
            return

        cur_time = new_message.date.strftime("%Y-%m-%d %H:%M")

        new_balance = balance - PRICE

        try:
            botDB.update_balance(call.from_user.id, new_balance)
        except Exceptions.NotEnoughMoneyError:
            call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                       text=SOMETHING_WENT_WRONG_TEXT, reply_markup=get_back_to_main_menu_keyboard())
            return

        client = botDB.get_client(call.from_user.id, device_num)
        extended = Files.update_server_config_file(client)

        if not extended:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=new_message.message_id,
                                             text=SOMETHING_WENT_WRONG_TEXT,
                                             reply_markup=get_back_to_main_menu_keyboard())
            return

        botDB.add_transaction(call.from_user.id, 0, PRICE, cur_time,
                              f"Продление прописки: \"Устройство №{device_num}\"")

        Files.write_to_logs(
            f"user {call.from_user.username} {call.from_user.id} extended subscription fot device №{device_num}")

        next_date = DateFunc.get_next_date(new_message.date.strftime("%Y-%m-%d"))

        botDB.change_client_activity(call.from_user.id, device_num, 1)
        botDB.update_client_end_date(call.from_user.id, device_num, next_date)

        await call.bot.delete_message(call.from_user.id, new_message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f"Подписка для устройства №{device_num} успешно продлена.\nС вашего счета списано {PRICE}₽. "
                                         f"Следующее списание будет произведено автоматически {transform_date_string_format(next_date)}.\n"
                                         f"В случае недостатка средств подписка будет приостановлена и доступ к vpn ограничен.",
                                    reply_markup=get_back_to_main_menu_keyboard())

    elif call.data == PROMOCODES_CALLBACK:
        botDB.set_promo_flag(call.from_user.id, 1)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"Введите промокод",
                                         reply_markup=get_back_to_previous_menu_from_callbacks_keyboard())

    elif call.data == BACK_TO_PREV_MENU_FROM_PROMO_CALLBACK:
        botDB.set_promo_flag(call.from_user.id, 0)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())

    # finance

    elif call.data == FINANCE_CALLBACK:
        balance = botDB.get_balance(call.from_user.id)
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"На Вашем счете: {balance}₽.", reply_markup=get_finance_keyboard())

    elif call.data == PAYMENTS_HISTORY_CALLBACK:
        user_data_file_path = get_user_payments_history(call.from_user.id)
        with open(user_data_file_path, 'rb') as file:
            file_data = BytesIO(file.read())
            await call.bot.send_document(chat_id=call.from_user.id, document=InputFile(file_data,
                                                                                       filename='balance history.txt'))  # todo добавить какой-нибудь текст
        await call.bot.delete_message(call.from_user.id, call.message.message_id)
        await call.bot.send_message(call.from_user.id, MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())

    elif call.data == FILL_UP_CALLBACK:
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="Выберите, на какую сумму пополнить баланс",
                                         reply_markup=get_fill_up_balance_keyboard())

    elif call.data in FILL_UP_BALANCE_CALLBACKS_MAP:
        sum_value = FILL_UP_BALANCE_CALLBACKS_MAP[call.data]
        balance = botDB.get_balance(call.from_user.id)
        if balance + sum_value > 300:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text=f"Поскольку бот работает в тестовом режиме, сумма средств на счете временно ограничена 300₽.\n"
                                                  f"На вашем счете: {balance}₽.",
                                             reply_markup=get_back_to_main_menu_keyboard())
            return
        new_balance = balance + sum_value
        balance_updated = botDB.update_balance(call.from_user.id, new_balance)
        if balance_updated:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text=f"Ваш баланс успешно пополнен на {sum_value}₽.",
                                             reply_markup=get_back_to_main_menu_keyboard())

            botDB.add_transaction(call.from_user.id, 1, sum_value, DateFunc.get_cur_time(),
                                  'Пополнение баланса')

            Files.write_to_logs(f"user {call.from_user.id} filled up balance for {sum_value}₽.")
        else:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text=SOMETHING_WENT_WRONG_TEXT,
                                             reply_markup=get_back_to_main_menu_keyboard())
            Files.write_to_logs(f"failed to fill up balance for {sum_value}₽ for user {call.from_user.id}")

    elif call.data == INVITING_LINKS_CALLBACK:
        uniq_link = BASE_URL + f'?start={call.from_user.id}'
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="Вы можете пригласить друзей и получить 50₽ за каждого нового пользователя, "
                                              f"перешедшего по вашей пригласительной ссылке: {uniq_link}",
                                         reply_markup=get_back_to_main_menu_keyboard())


async def fill_up_balance_actions_for_message(message: types.Message, delta_value: int, promo_use: bool,
                                              to_user_id: int | None = None):
    if promo_use:
        send_text = f"Промокод успешно применен. Ваш баланс пополнен на {delta_value}₽."
        trans_text = "Применение промокода"
        to_user_id = message.from_user.id
    else:
        send_text = f"Вам начислено {delta_value}₽ за приглашение нового пользователя."
        trans_text = "Приглашение нового пользователя"
    balance = botDB.get_balance(to_user_id)
    new_balance = balance + delta_value
    balance_updated = botDB.update_balance(to_user_id, new_balance)

    if balance_updated:
        await message.bot.send_message(chat_id=to_user_id,
                                       text=send_text,
                                       reply_markup=get_back_to_main_menu_keyboard())
        botDB.add_transaction(to_user_id, 1, delta_value, DateFunc.get_cur_time(),
                              trans_text)
        if promo_use:
            Files.write_to_logs(f"user {message.from_user.id} used promocode for {delta_value}₽")
        return True
    else:
        await message.bot.send_message(chat_id=to_user_id,
                                       text=SOMETHING_WENT_WRONG_TEXT,
                                       reply_markup=get_back_to_main_menu_keyboard())
        Files.write_to_logs(f"user {message.from_user.id} failed to use promocode for {delta_value}₽")
        return False


@bot.message_handler()
async def answer_message(message: types.Message):
    promo_flag = botDB.get_promo_flag(message.from_user.id)
    botDB.set_promo_flag(message.from_user.id, 0)
    if not promo_flag:
        return

    used_promocodes = botDB.get_used_promocodes(message.from_user.id)
    if message.text in used_promocodes:
        await message.bot.send_message(message.from_user.id, "Вы уже воспользовались этим промокодом.",
                                       reply_markup=get_back_to_previous_menu(BACK_TO_MAIN_MENU_CALLBACK))
        return

    if message.text not in PROMOCODES:
        await message.bot.send_message(message.from_user.id, "Кажется, такого промокода не существует.",
                                       reply_markup=get_back_to_previous_menu(BACK_TO_MAIN_MENU_CALLBACK))
        return

    promo_value = PROMOCODES[message.text]
    updated = await fill_up_balance_actions_for_message(message, promo_value, promo_use=True)
    if updated:
        botDB.add_used_promocode(message.from_user.id, message.text)
    Files.write_to_logs(
        f"Пользователь {message.from_user.id} воспользовался промокодом {message.text} и получил {promo_value}₽")
