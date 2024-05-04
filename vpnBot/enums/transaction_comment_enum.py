from enum import Enum


class TransactionCommentEnum(Enum):
    START_BALANCE = 'Стартовый баланс'
    FILL_UP_BALANCE = 'Пополнение баланса'
    ADD_DEVICE = 'Добавлено устройство №{}'
    SUBSCRIPTION = 'Продление подписки: устройство №{}'
    PROMO_CODE = 'Применение промокода'
    INVITATION = 'Приглашение пользователя'
