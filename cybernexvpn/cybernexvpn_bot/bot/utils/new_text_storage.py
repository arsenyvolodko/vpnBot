from cybernexvpn.cybernexvpn_bot import config
from cybernexvpn.cybernexvpn_bot.config import START_BALANCE

FIRST_USAGE_TEXT = (
    "Привет! Этот бот предоставляет доступ к быстрому и классному vpn.\n"
    f"На твоем балансе {START_BALANCE}₽, чтобы ты мог попробовать первый месяц бесплатно!"
)

WEB_PANEL_INFO_TEXT = (
    "💡 Если у тебя не получится воспользоваться ботом в Telegram (например, чтобы пополнить баланс или продлить подписку), ты всегда можешь сделать это через нашу веб-страницу управления.\n"
    "Закрепил сообщение, так что ты легко найдёшь его даже без VPN ;)"
)
WEB_PANEL_BTN_TEXT = "Перейти в веб"

SUCCESSFUL_INVITATION_INFO_MSG = (
    f"Тебе начислено {config.INVITATION_BONUS}₽ "
    "за приглашение нового пользователя {}"
)

MAIN_MENU_TEXT_FROM_START = 'Отлично!\nТеперь, чтобы подключить vpn, нажми на кнопку "Устройста" в меню ниже, а затем на кнопку "Добавить устройство"'

MAIN_MENU_TEXT = "Меню\n"

SERVERS_LOST_RECOVERY_TEXT = (
    "К сожалению, из-за технических неполадок на стороне провайдера серверов "
    "доступ к прежним устройствам временно утерян.\n\n"
    "Подробнее о ситуации можно прочитать в канале: @cybernexvpn\n\n"
    "Мне очень жаль, что так произошло. Чтобы вы не оставались без доступа "
    "к важным ресурсам, сейчас можно бесплатно добавить новое устройство через меню ниже.\n\n"
    "Если работа старых серверов восстановится, ваши прежние устройства автоматически "
    "появятся в меню вместе с новыми. Баланс и подписки также будут восстановлены при первой возможности.\n\n"
    "Пожалуйста, добавьте новое устройство в меню ниже."
)

NO_DEVICES_ADDED = "У тебя пока нет добавленных устройств"

CHOOSE_DEVICE_TYPE = "Выбери тип устройства:"

CHOOSE_DEVICE = "Выбери устройство:"

CHOOSE_REGION = "Выбери сервер"

USER_NOT_FOUND_ERROR_MSG = (
    "Упс! Кажется что-то пошло не так. Пожалуйста, вернитесь в меню и попробуйте снова."
)
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

SERVER_HAS_NO_FREE_IPS = (
    "К сожалению, на этом сервере временно закончились свободные ip-адреса(\n"
    "Пожалуйста, выбери другой сервер."
)

BALANCE_INFO = "Твой баланс: {}₽"

CHOOSE_SUM_TO_FILL_UP_BALANCE = "На какую сумму ты хочешь пополнить баланс?"

CHECKING_ADDING_DATA = "Проверяю данные.."
ADDING_DEVICE = "Добавляю устройство.."
DEVICE_SUCCESSFULLY_ADDED = "Устройство успешно добавлено"

DELETING_DEVICE = "Удаляю устройство.."
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
PAYMENT_SUCCESSFULLY_PROCESSED = "Твой баланс успешно пополнен!"
PAYMENT_SUCCESSFULLY_PROCESSED_WITH_VALUE = "Твой баланс успешно пополнен на {}₽"
FUNDS_DEBITED_SUM = "С твоего счета успешно списано {}₽"

GETTiNG_CONNECTION_DATA = "Получаю данные.."

REACTIVATE_DEVICE_AFTER_FILL_UP = ("У тебя неактивна подписка на одно устройство.\n"
                                   "<b>Для того, чтобы возобновить подписку, нажми на это устройство ниже</b>")

REACTIVATE_DEVICES_AFTER_FILL_UP = ("У тебя неактивна подписка для нескольких устройств.\n"
                                    "<b>Для того, чтобы возобновить подписку на устройство, "
                                    "выбери его из списка ниже</b>")

REACTIVATING_DEVICE = "Возобновляю подписку.."

WINDOWS_CONNECTION_INSTRUCTION = (
    '1️⃣Скачай <a href="https://www.wireguard.com/install/">приложение</a> Wireguard\n'
    "2️⃣Скачай файл в сообщении выше\n"
    '3️⃣Открой Wireguard, нажми "Добавить туннель" и выбери скачанный файл\n'
)

MACOS_CONNECTION_INSTRUCTION = (
    '1️⃣Скачай <a href="https://apps.apple.com/ru/app/wireguard/id1451685025?mt=12">приложение</a> Wireguard\n'
    "2️⃣Скачай файл в сообщении выше\n"
    '3️⃣Открой Wireguard, нажми "Импорт туннеля из файла" и выбери скачанный файл\n'
)

ANDROID_CONNECTION_INSTRUCTION = (
    '1️⃣Скачай <a href="https://play.google.com/store/apps/details?id=com.wireguard.android">приложение</a> Wireguard\n'
    "2️⃣Открой qr код на другом устройстве\n"
    '3️⃣Открой приложение wireguard на телефоне, нажми на "+" или "Добавить туннель", а затем выбери "Импорт туннеля из qr-кода"\n'
    '4️⃣Отсканируй qr код и введи любое название для туннеля, например "vpn"\n\n'
    'Ура! Теперь можно смотреть рилсы!'
)

IPHONE_CONNECTION_INSTRUCTION = (
    '1️⃣Скачай <a href="https://apps.apple.com/us/app/wireguard/id1441195209">приложение</a> Wireguard\n'
    "2️⃣Сделай 5 тыков, как показано на фото выше (оно того стоит..)\n\n"
    "Ура! Теперь можно смотреть рилсы!"
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

IS_EVERYTHING_OK = "Все получилось?"

IS_EVERYTHING_OK_2 = ("Теперь все получилось?\n"
                      f'Если все еще есть проблемы, то напиши <a href="{config.ADMIN_TG_URL}">мне</a>, я обязательно помогу!')

WHAT_IS_WRONG_QUESTION = (
    "В чем проблема?\n"
    "1️⃣Не выходит добавить файл, как описано в инструкции\n"
    "2️⃣Получилось добавить файл в приложение, но vpn не работает\n"
    "3️⃣Другое\n"
)

TEXT_ME = f'Напиши <a href="{config.ADMIN_TG_URL}">мне</a>, в чем проблема, я обязательно помогу!'

ANDROID_ALTERNATIVES = (
    '1️⃣Скачай <a href="https://play.google.com/store/apps/details?id=com.wireguard.android">приложение</a> Wireguard\n'
    '2️⃣Скачай файл в сообщении выше и открой Wireguard\n'
    '3️⃣Нажми на "+" или "Добавить туннель", а затем выбери "Импорт туннеля из файла"\n\n'
    "Ура! Теперь можно смотреть рилсы!"
)
