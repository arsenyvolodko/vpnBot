import time

from Exceptions.NotEnoughMoneyError import NotEnoughMoneyError
from Ips import Ips
from system.dispatcher import bot
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

    await message.bot.send_message(message.from_user.id, MAIN_MENU_TEXT,
                                   reply_markup=get_main_menu_keyboard())

    if not botDB.user_exists(message.from_user.id):
        botDB.update_balance(message.from_user.id, PRICE)


def get_next_date(date_string: str = None, months: int = 1):
    if not date_string:
        date_string = datetime.now().strftime("%Y-%m-%d")
    date = datetime.strptime(date_string, "%Y-%m-%d")
    delta = relativedelta(months=months)
    next_payment_date = date.replace(day=date.day) + delta
    return next_payment_date.strftime("%Y-%m-%d")


def check_balance(user_id: int, expected_balance: float):
    balance = botDB.get_balance(user_id)
    if balance >= expected_balance:
        return True
    return balance


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


    if call.data == ADD_FIRST_DEVICE_CALLBACK:
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="После добавления устройства с вашего счета автоматически спишется сумма, "
                                              "соответсвующая стоимости подписки в месяц за одно устройство - 100₽.\n"
                                              "Убедитесь, что на вашем счету достаточно средств.",
                                         reply_markup=get_add_device_confirmation_keyboard())


    if call.data == ADD_FIRST_DEVICE_CONFIRMED_CALLBACK:
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text="Проверяем данные. Это займет несколько секунд.")

        balance = botDB.get_balance(call.from_user.id)
        if balance < PRICE:
            await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text="На вашем счете недостаточно средств для подключения нового устройства. "
                                                  "Стоимость подписки списывается автоматически после добавления устройства.\n"
                                                  f"Стоимость подписки: 100₽ в месяц.\n"
                                                  f"На вашем счете: {balance}₽.",
                                             reply_markup=get_not_enough_money_keyboard())
            return

        next_date = get_next_date()

        cur_time = datetime.now().strftime("%y.%m.%d %H:%M")
        try:
            botDB.add_transaction(call.from_user.id, 0, PRICE, cur_time)
        except NotEnoughMoneyError :
            call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                       text=SOMETHING_WENT_WRONG_TEXT, reply_markup=get_back_to_main_menu_keyboard())
            return

        keys = Keys()
        ips = botDB.get_next_free_ips()

        client = Client(call.from_user.id, 1, ips, keys, next_date)
        botDB.add_client_to_db(client)
        config_file_path, qr_code_file_path = Files.create_client_config_file(client)

        await call.bot.send_document(call.from_user.id, ('NexVpn.conf', config_file_path))
        await call.bot.send_photo(call.from_user.id, open(f'{qr_code_file_path}', 'rb'))

        await call.bot.delete_message(call.from_user.id, call.message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                         text="Новое устройство успешно добавлено. С вашего счета списано 100₽. "
                                         f"Следующее списание будет произведено автоматически {next_date.replace('_', '.')}.\n"
                                         f"В случае недостатка средств подписка будет приостановлена и доступ к vpn ограничен.\n"
                                         f"При пополнении баланса подписка будет вновь активирована.",
                                         reply_markup=get_back_to_main_menu_keyboard())

        Files.update_server_config_file(client)


    if 'specific_device_callback#' in call.data:
        device_num = int(re.sub('specific_device_callback#', '', call.data))
        await call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                         text=f"Устройство №{device_num}:",
                                         reply_markup=get_specific_device_keyboard())


    if call.data == GET_QR_AND_CONFIG_CALLBACK:
        device_num = int(re.sub('Устройство №', '', call.message.text)[:-1])
        client = botDB.get_client(call.from_user.id, device_num)
        config_file_path, qr_code_file_path = Files.create_client_config_file(client)
        await call.bot.delete_message(call.from_user.id, call.message.message_id)
        await call.bot.send_document(call.from_user.id, ('NexVpn.conf', config_file_path))
        await call.bot.send_photo(call.from_user.id, open(f'{qr_code_file_path}', 'rb'))
        await call.bot.send_message(call.from_user.id, MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard())

    if call.data == DELETE_DEVICE_CALLBACK:
        device_num = int(re.sub('Устройство №', '', call.message.text)[:-1])
        client = botDB.get_client(call.from_user.id, device_num)
        removed_from_server_config = Files.remove_client(client)
        removed_from_db = botDB.remove_client_from_db(client.user_id, client.device_num)

        if not removed_from_db or not removed_from_server_config:
            call.bot.edit_message_text(call.from_user.id, call.message.message_id,
                                       SOMETHING_WENT_WRONG_TEXT, get_back_to_main_menu_keyboard())
            return

        call.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                   text=f'{call.message.text[:-1]} успешно удалено', reply_markup=get_back_to_main_menu_keyboard())

        if not botDB.add_free_ips(client.ips):
            time.sleep(3)
            if not botDB.add_free_ips(client.ips):
                return  # todo inform me that cannot add new ips
