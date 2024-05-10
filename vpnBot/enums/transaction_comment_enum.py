from enum import Enum


class TransactionCommentEnum(Enum):
    START_BALANCE = 'Стартовый баланс'
    FILL_UP_BALANCE = 'Пополнение баланса'
    ADD_DEVICE = 'Добавление устройства'  # todo maybe add device_num
    SUBSCRIPTION = 'Продление подписки: устройство №{}'  # todo formatting doesn't work
    PROMO_CODE = 'Применение промокода'
    INVITATION = 'Приглашение пользователя'
