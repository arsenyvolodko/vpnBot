from enum import Enum


class TransactionCommentEnum(Enum):
    RENEW_SUBSCRIPTION = "Продление подписки"
    INVITATION = "Приглашение пользователя"
    START_BALANCE = "Стартовый баланс"
    FILL_UP_BALANCE = "Пополнение баланса"
    ADD_DEVICE = "Добавление устройства"
    PROMO_CODE = "Применение промокода"
    UPDATED_BY_ADMIN = "Изменено администратором"
