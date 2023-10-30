PRICE = 100  # ₽

BACK_TO_MAIN_MENU_TEXT = 'Вернуться в меню'
BACK_TO_MAIN_MENU_CALLBACK = 'back_to_main_menu_callback'
BACK_TO_PREV_MENU_TEXT = 'Назад'
CONTINUE_TEXT = 'Продолжить'
MY_ID = 506954303


MAIN_MENU_TEXT = '''
Меню\n
Для добавления нового устройства или удаления существующего, перейдите в раздел "Устройства".\n
Для пополнения баланса или просмотра истории транзакций, перейдите в раздел "Финансы".'''

START_TEXT = f'''
Привет! Этот бот предоставляет специальные ключи для подключения к VPN через приложение Wireguard.\n
Уникальные алгоритмы шифрования и маршрутизации не снижают скорость интернета, а также обеспечивают мгновенное подключение к VPN.\n
На вашем балансе {PRICE}₽, чтобы Вы могли попробовать первый месяц бесплатно.\n
Для начала, нужно скачать приложение Wireguard, а затем перейти в меню.
'''

# PATHS
PATH_TO_CONFIG = "some_dir/server.conf"
PATH_TO_META = "meta_configs"
PATH_TO_LOGS = 'logs.txt'
PATH_TO_CLIENTS_FILES = 'client_files'


DEVICES_TEXT = 'Устройства'
DEVICES_CALLBACK = 'devices_callback'

ADD_DEVICE_TEXT = 'Добавить устройство'
ADD_DEVICE_CALLBACK = 'add_device_callback'
ADD_DEVICE_CONFIRMED_CALLBACK = 'add_device_confirmed_callback'

# SPECIFIC_DEVICE_CALLBACK = 'specific_device_callback'
GET_QR_AND_CONFIG_TEXT = 'Получить файл и qr'
GET_QR_AND_CONFIG_CALLBACK = 'get_qr_and_config_callback'
DELETE_DEVICE_TEXT = 'Удалить устройство'
DELETE_DEVICE_CALLBACK = 'delete_device_callback'

DELETE_DEVICE_CONFIRM_TEXT = 'Удалить'
DELETE_DEVICE_CONFIRM_CALLBACK = 'delete_device_confirm_callback'
DELETE_DEVICE_CANCEL_TEXT = 'Отмена'

EXTEND_SUBSCRIPTION_FOR_DEVICE_TEXT = 'Продлить подписку'
EXTEND_SUBSCRIPTION_FOR_DEVICE_CALLBACK = 'extend_subscription_for_device_callback'
EXTEND_SUBSCRIPTION_FOR_DEVICE_CONFIRM_CALLBACK = 'extend_subscription_for_device_confirm_callback'

FINANCE_TEXT = 'Финансы'
FINANCE_CALLBACK = 'finance_callback'
FILL_UP_TEXT = 'Пополнить баланс'
FILL_UP_CALLBACK = 'fill_up_balance'
PAYMENTS_HISTORY_TEXT = 'История транзакций'
PAYMENTS_HISTORY_CALLBACK = 'payments_history_callback'

FILL_UP_BALANCE_100_TEXT = '100₽'
FILL_UP_BALANCE_200_TEXT = '200₽'
FILL_UP_BALANCE_300_TEXT = '300₽'
FILL_UP_BALANCE_500_TEXT = '500₽'
FILL_UP_BALANCE_700_TEXT = '700₽'
FILL_UP_BALANCE_1000_TEXT = '1000₽'

FILL_UP_BALANCE_100_CALLBACK = 'fill_up_balance_100_callback'
FILL_UP_BALANCE_200_CALLBACK = 'fill_up_balance_200_callback'
FILL_UP_BALANCE_300_CALLBACK = 'fill_up_balance_300_callback'
FILL_UP_BALANCE_500_CALLBACK = 'fill_up_balance_500_callback'
FILL_UP_BALANCE_700_CALLBACK = 'fill_up_balance_700_callback'
FILL_UP_BALANCE_1000_CALLBACK = 'fill_up_balance_1000_callback'

FILL_UP_BALANCE_CALLBACKS_MAP = {FILL_UP_BALANCE_100_CALLBACK: 100, FILL_UP_BALANCE_200_CALLBACK: 200,
                                 FILL_UP_BALANCE_300_CALLBACK: 300, FILL_UP_BALANCE_500_CALLBACK: 500,
                                 FILL_UP_BALANCE_700_CALLBACK: 700, FILL_UP_BALANCE_1000_CALLBACK: 1000}

SOMETHING_WENT_WRONG_TEXT = 'К сожалению, что-то пошло не так :(\n' \
                            'Видимо, автор бота не умеет в БД.. пожалуйста, вернитесь в меню и попробуйте еще раз.'
