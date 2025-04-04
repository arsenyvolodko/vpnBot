from abc import ABC

from cybernexvpn.cybernexvpn_bot.bot.keyboards.button import Button


class ButtonsTextStorage(ABC):
    GO_TO_MAIN_MENU = "Перейти в меню"
    GO_BACK_TO_MAIN_MENU = "Вернуться в меню"
    GO_BACK_TO_MAIN_MENU_WITH_NEW_MESSAGE = GO_BACK_TO_MAIN_MENU
    GO_TO_MAIN_MENU_FROM_START = GO_TO_MAIN_MENU

    GO_BACK = "Назад"
    CANCEL_STATE = "Отмена ❌"
    CONTINUE = "Продолжить ▶️"

    SERVER = ""

    DEVICES = "Устройства 📱"
    FINANCE = "Финансы 💰"
    PROMO_CODE = "Применить промокод 💸"
    INVITATION_LINK = "Пригласительные ссылки 💌"

    DEVICE = "Устройство №{}"
    EDIT_DEVICE = "Редактировать ✏️"
    ADD_DEVICE = "Добавить устройство ➕"

    EDIT_DEVICE_AUTO_RENEW = "Авто-продление: {}"
    EDIT_DEVICE_NAME = "Переименовать ✏️"
    EDIT_DEVICE_TYPE = "Изменить тип устройства 📱-> 💻"
    GET_CONNECTION_DATA = "Данные для подключения 📂"
    DELETE_DEVICE = "Удалить устройство 🗑"
    DELETE_DEVICE_CONFIRMATION = "Продолжить ▶️"

    GET_QR_CODE = "Использовать QR-код"

    GET_TRANSACTIONS_HISTORY = "История транзакций 🧾"
    FILL_UP_BALANCE = "Пополнить баланс 💳"

    FILL_UP_BALANCE_VALUE = ""

    REACTIVATE_DEVICE = "Возобновить подписку 🔄"

    WITHOUT_QR = "Хочу без QR-кода"

    ADDING_DEVICE_PROBLEMS = "Что-то не так 🤔"
    ADDING_DEVICE_OK = "Все работает 🎉"


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

    DEVICES = Button()
    FINANCE = Button()
    PROMO_CODE = Button()
    INVITATION_LINK = Button()

    SERVER = Button()

    DEVICE = Button()
    EDIT_DEVICE = Button()
    ADD_DEVICE = Button()

    EDIT_DEVICE_AUTO_RENEW = Button()
    EDIT_DEVICE_NAME = Button()
    EDIT_DEVICE_TYPE = Button()
    GET_CONNECTION_DATA = Button()
    DELETE_DEVICE = Button()
    DELETE_DEVICE_CONFIRMATION = Button()
    GET_QR_CODE = Button()

    GET_TRANSACTIONS_HISTORY = Button()
    FILL_UP_BALANCE = Button()

    FILL_UP_BALANCE_VALUE = Button()
    REACTIVATE_DEVICE = Button()

    ADDING_DEVICE_PROBLEMS = Button()
    ADDING_DEVICE_OK = Button()

    WITHOUT_QR = Button()
