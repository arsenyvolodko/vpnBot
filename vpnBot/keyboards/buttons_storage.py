from abc import ABC

from vpnBot.keyboards.button import Button


class ButtonsTextStorage(ABC):
    GO_TO_MAIN_MENU = "Перейти в меню"
    GO_BACK_TO_MAIN_MENU = "Вернуться в меню"
    GO_BACK_TO_MAIN_MENU_WITH_NEW_MESSAGE = "Вернуться в меню"
    GO_TO_MAIN_MENU_FROM_START = "Перейти в меню"

    GO_BACK = "Назад"
    CANCEL_STATE = "Отмена"
    CONTINUE = "Продолжить"

    WG_APP_ANDROID = "Android"
    WG_APP_IOS = "IOS"
    WG_APP_PC = "PC"

    DEVICES = "Устройства 📱"
    FINANCE = "Финансы 💳"
    PROMO_CODE = "Применить промокод"
    INVITATION_LINK = "Пригласительные ссылки"

    DEVICE = "Устройство №{}"
    ADD_DEVICE = "Добавить устройство"
    ADD_DEVICE_CONFIRMATION = "Продолжить"

    GET_DEVICES_CONFIG_AND_QR = "Получить конфиг и qr + инструкция"
    DELETE_DEVICE = "Удалить устройство"
    DELETE_DEVICE_CONFIRMATION = "Продолжить"

    GET_TRANSACTIONS_HISTORY = "История транзакций"
    FILL_UP_BALANCE = "Пополнить баланс"

    FILL_UP_BALANCE_VALUE = ""

    RESUME_DEVICE_SUBSCRIPTION = "Возобновить подписку"


class AutoNameButtonMeta(type):
    def __new__(cls, name, bases, namespace):
        for attr_name, value in namespace.items():
            if isinstance(value, Button):
                if not value.name:
                    value.name = attr_name
                if not value.txt:
                    value.txt = getattr(ButtonsTextStorage, value.name)
        return type.__new__(cls, name, bases, namespace)


class ButtonsStorage(metaclass=AutoNameButtonMeta):
    GO_TO_MAIN_MENU = Button()
    GO_BACK_TO_MAIN_MENU = Button()
    GO_BACK_TO_MAIN_MENU_WITH_NEW_MESSAGE = Button()
    GO_TO_MAIN_MENU_FROM_START = Button()
    GO_BACK = Button()

    CANCEL_STATE = Button()
    CONTINUE = Button()

    WG_APP_ANDROID = Button()
    WG_APP_IOS = Button()
    WG_APP_PC = Button()

    DEVICES = Button()
    FINANCE = Button()
    PROMO_CODE = Button()
    INVITATION_LINK = Button()

    DEVICE = Button()
    ADD_DEVICE = Button()
    ADD_DEVICE_CONFIRMATION = Button()

    GET_DEVICES_CONFIG_AND_QR = Button()
    DELETE_DEVICE = Button()
    DELETE_DEVICE_CONFIRMATION = Button()

    GET_TRANSACTIONS_HISTORY = Button()
    FILL_UP_BALANCE = Button()

    FILL_UP_BALANCE_VALUE = Button()
    RESUME_DEVICE_SUBSCRIPTION = Button()
