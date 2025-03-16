from cybernexvpn.cybernexvpn_bot import config
from cybernexvpn.cybernexvpn_bot.config import START_BALANCE

FIRST_USAGE_TEXT = (
    "Привет! Этот бот предоставляет доступ к быстрому и классному vpn.\n"
    f"На твоем балансе {START_BALANCE}₽, чтобы ты мог попробовать первый месяц бесплатно!"
)

SUCCESSFUL_INVITATION_INFO_MSG = (
    f"Тебе начислено {config.INVITATION_BONUS}₽ "
    "за приглашение нового пользователя {}"
)

MAIN_MENU_TEXT_FROM_START = 'Отлично!\nТеперь, чтобы подключить vpn, нажми на кнопку "Устройста" в меню ниже, а затем на кнопку "Добавить устройство"'

MAIN_MENU_TEXT = (
    "Меню\n"
)

NO_DEVICES_ADDED = "У тебя пока нет добавленных устройств"

CHOOSE_DEVICE_TYPE = "Выбери тип устройства:"

CHOOSE_DEVICE = "Выбери устройство:"

CHOOSE_REGION = "Выбери страну:"

USER_NOT_FOUND_ERROR_MSG = "Упс! Кажется что-то пошло не так. Попробуй набрать команду /start"
SERVER_NOT_FOUND_ERROR_MSG = "Упс! Похоже, такой сервер больше не доступен"
CLIENT_NOT_FOUND_ERROR_MSG = "Упс! Похоже, это устройство больше не доступно"
CLIENT_ALREADY_DELETED_ERROR_MSG = "Упс! Похоже, это устройство уже удалено"

SOMETHING_WENT_WRONG_ERROR_MSG = (
    "К сожалению, что-то пошло не так :( \nПопробуй повторить операцию еще раз"
)

NOT_ENOUGH_MONEY_ERROR_MSG = (
    "К сожалению, у тебя недостаточно средств для выполнения этой операции.\n"
    "Твой баланс: {}₽"
)

SERVER_DESCRIPTION = "Страна: {}\n" "Стоимость: {}₽/месяц\n"

NO_SERVERS_AVAILABLE = (
    "К сожалению, на данный момент нет доступных серверов(\nВозвращайся позже."
)

BALANCE_INFO = "Твой баланс: {}₽"

CHOOSE_SUM_TO_FILL_UP_BALANCE = "На какую сумму ты хочешь пополнить баланс?"

DEVICE_SUCCESSFULLY_ADDED = "Устройство успешно добавлено"
DEVICE_SUCCESSFULLY_DELETED = "Устройство успешно удалено"

ACTIVE = "Активно 🟢"
INACTIVE = "Не активно 🔴"

SPECIFIC_ACTIVE_DEVICE_INFO_TEXT = (
    "<b>{name}</b>:\n"
    "Тип устройства: {type}\n"
    "Статус: {status}\n"
    "Авто-продление: {auto_renew}\n"
    "Локация: {server}\n"
    "Стоимость: {price}₽/месяц\n"
    "Следующее списание: {date}\n"
)

SPECIFIC_INACTIVE_DEVICE_INFO_TEXT = (
    "<b>{name}</b>:\n"
    "Тип устройства: {type}\n"
    "Статус: {status}\n"
    "Локация: {server}\n"
    "Стоимость: {price}₽/месяц\n"
    "<b>Устройство будет удалено {date}, если не возобновить подписку.</b>"
)

EDIT_ACTIVE_DEVICE_TEXT = (
    "Название: «{name}»\n" "Тип устройства: {type}\n" "Авто-продление: {auto_renew}\n"
)

EDIT_INACTIVE_DEVICE_TEXT = "Название: {name}\n" "Тип устройства: {type}\n"


DELETE_DEVICE_CONFIRMATION_INFO = "Ты уверен, что хочешь удалить устройство? Это действие необратимо и доступ к vpn будет ограничен сразу после удаления"

AUTO_RENEW_ON = "Авто-продление включено"
AUTO_RENEW_OFF = "Авто-продление выключено"

INPUT_NEW_DEVICE_NAME = "Как назовем устройство?"
DEVICE_SUCCESSFULLY_RENAMED = "Устройство успешно переименовано"
DEVICE_TYPE_SUCCESSFULLY_CHANGED = "Тип устройства успешно изменен"

INPUT_PROMO_CODE = "Введи промокод"
PROMO_CODE_SUCCESSFULLY_APPLIED = (
    "Промокод успешно применен!\nВаш баланс пополнен на {}₽"
)
PROMO_CODE_NOT_FOUND_ERROR_MSG = "Похоже, такого промокода не существует"


FILL_UP_BALANCE_INFO_MSG = "Пополнение баланса на {}₽"

INVITATION_LINK_INFO_MSG = (
    f"Ты можешь пригласить знакомых и получить {config.INVITATION_BONUS}₽ за каждого нового пользователя, "
    "перешедшего по твоей пригласительной ссылке: {}"
)

SET_CORRECT_DEVICE_TYPE = "Для того, чтобы продолжить, необходимо выбрать тип устройства. Впоследствии ты сможешь изменить его в настройках устройства"

DEVICE_ALREADY_ACTIVE = "Устройство уже активно"
DEVICE_SUCCESSFULLY_REACTIVATED = (
    "Подписка на устройство успешно возобновлена! С твоего счета списано {}₽"
)
TO_PAY_BTN_LINK_TEXT = "Оплатить"
PAYMENT_SUCCESSFULLY_PROCESSED = "Твой баланс успешно пополнен на {}₽"

GETTiNG_CONNECTION_DATA = "Получаю данные.."

WINDOWS_CONNECTION_INSTRUCTION = (
    '1. Скачай <a href="https://www.wireguard.com/install/">приложение</a> Wireguard\n'
    '2. Скачай файл в сообщении выше\n'
    '3. Открой Wireguard, нажми "Добавить туннель" и выбери скачанный файл\n'
)

MACOS_CONNECTION_INSTRUCTION = (
    '1. Скачай <a href="https://apps.apple.com/ru/app/wireguard/id1451685025?mt=12">приложение</a> Wireguard\n'
    '2. Скачай файл в сообщении выше\n'
    '3. Открой Wireguard, нажми на плюсик в левом нижнем углу и выбери скачанный файл\n'
)

ANDROID_CONNECTION_INSTRUCTION = (
    '1. Скачай <a href="https://play.google.com/store/apps/details?id=com.wireguard.android">приложение</a> Wireguard\n'
    '2. Открой файл в сообщении выше и поделись им в приложение Wireguard\n'
    'Или используй QR-код, нажав на кнопку ниже, если у тебя есть возможность открыть его на другом устройстве.\n'
)

IPHONE_CONNECTION_INSTRUCTION = (
    '1. Скачай <a href="https://apps.apple.com/us/app/wireguard/id1441195209">приложение</a> Wireguard\n'
    '2. Сделай 5 тыков, как показано на фото выше (поверь, оно того стоит..)\n'
    '3. Ура! Теперь можно смотреть рилсы!'
)

ANDROID_NAME_CHOICES = [
    "cybernexvpn",
    "cybernexVpn",
    "cybernexVPN",
    "cyberNexvpn",
    "cyberNexVpn",
    "cyberNexVPN",
    "Cybernexvpn",
    "CybernexVpn",
    "CybernexVPN",
    "CyberNexvpn",
    "CyberNexVpn",
    "CyberNexVPN",
]
