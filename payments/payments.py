import os
import uuid
from pprint import pprint

from yookassa import Payment, Configuration, Webhook
from yookassa.domain.response import PaymentResponse
from dotenv import load_dotenv

load_dotenv()

Configuration.account_id = int(os.environ.get('YOOKASSA_SHOP_ID'))
Configuration.secret_key = os.environ.get('YOOKASSA_TOKEN')
Configuration.configure_auth_token(os.environ.get('YOOKASSA_OAUTH_TOKEN'))


def create_payment(value: int) -> PaymentResponse:
    payment = Payment.create({
        "amount": {
            "value": f"{value}.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/CyberNexVpnBot"
        },
        "capture": True,
        "description": f"Пополнение баланса на {value} рублей"
    }, uuid.uuid4())
    return payment


# response = Webhook.add({
#     "event": "payment.succeeded",
#     "url": "https://www.example.com/notification_url",
# })
#

def fill_up_user_balance(user_id: int, value: int):
    payment = create_payment(value)
    payment_url = payment['confirmation']['confirmation_url']
    print(payment.json())


fill_up_user_balance(5, 1000)
