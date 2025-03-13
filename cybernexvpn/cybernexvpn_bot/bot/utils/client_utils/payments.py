from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient


async def gen_payment_url(user_id: int, value: int) -> str | None:
    async with CyberNexVPNClient() as api_client:
        request_schema = schemas.CreatePaymentRequest(value=value)
        payment_url_schema = await api_client.create_payment(user_id, request_schema)
        return payment_url_schema.url


async def get_transactions_history(user_id: int):
    async with CyberNexVPNClient() as api_client:
        return await api_client.get_transaction_history(user_id)
