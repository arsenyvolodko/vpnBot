from enum import Enum


class PaymentStatusEnum(Enum):
    PENDING = 'pending'
    WAITING_FOR_CAPTURE = 'waiting_for_capture'
    SUCCEEDED = 'succeeded'
    CANCELED = 'canceled'
    ERROR_AFTER_PAYMENT = 'error_after_payment'
