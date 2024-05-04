from abc import ABC

from vpnBot.static.common import PRICE


class TextsStorage(ABC):
    START_TEXT = \
        'Привет! Этот бот предоставляет специальные ключи для подключения к VPN через приложение Wireguard.' \
        'Уникальные алгоритмы шифрования и маршрутизации не снижают скорость интернета, а также обеспечивают мгновенное подключение к VPN.\n\n' \
        f'На вашем балансе {PRICE}₽, чтобы Вы могли попробовать первый месяц бесплатно.\n\n' \
        'Для начала, нужно скачать приложение Wireguard, а затем перейти в меню.'

    WG_APP_ANDROID_LINK = 'https://play.google.com/store/apps/details?id=com.wireguard.android'
    WG_APP_IOS_LINK = 'https://apps.apple.com/us/app/wireguard/id1441195209'
    WG_APP_PC_LINK = 'https://www.wireguard.com/install/'

    MAIN_MENU_TEXT = \
        'Меню\n' \
        'Для добавления нового устройства или удаления существующего, перейдите в раздел "Устройства".\n' \
        'Для пополнения баланса или просмотра истории транзакций, перейдите в раздел "Финансы".'

    CHOOSE_DEVICE = 'Выберите устройство:'
    NO_DEVICES_ADDED = 'У Вас пока нет добавленных устройств.'

    ADD_DEVICE_CONFIRMATION_INFO = \
        'После добавления устройства с вашего счета автоматически спишется сумма, ' \
        f'соответствующая стоимости подписки в месяц за одно устройство - {PRICE}₽.\n' \
        'На Вашем счете - {}₽.'
