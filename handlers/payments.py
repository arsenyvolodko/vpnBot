import os
import uuid

from yookassa import Payment, Configuration
from dotenv import load_dotenv

load_dotenv()

Configuration.account_id = int(os.environ.get('YOOKASSA_SHOP_ID'))
Configuration.secret_key = os.environ.get('YOOKASSA_TOKEN')

payment = Payment.create({
    "amount": {
        "value": "100.00",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": "https://t.me/CyberNexVpnBot"
    },
    "capture": True,
    "description": "Заказ №1"
}, uuid.uuid4())

# print(payment.status)
# print(payment.id)
# print(payment.json())

import requests

url = 'https://yookassa.ru/oauth/v2/authorize?response_type=code&client_id=vf8ebd5fn90l90rcu7nvjrruqqb4omjc&state=test-user'

response = requests.get(url)
print(response.status_code)
print(response.text)
print(response.json())
# LZMmEVtnnv11MSg4h2bzp16L1pbj3z-AeRxR75UxZd6hdsFCcg7thnDq6Ae3x9Zg

