from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.client import CyberNexVPNClient
from cybernexvpn.cybernexvpn_client.errors import ClientBaseError


async def apply_promo_code(user_id: int, promo_code: str) -> schemas.ApplyPromoCodeResponse | None:
    try:
        async with CyberNexVPNClient() as api_client:
            request_schema = schemas.ApplyPromoCodeRequest(code=promo_code)
            applied_promo_code: schemas.ApplyPromoCodeResponse = await api_client.apply_promo_code(user_id, request_schema)
        return applied_promo_code
    except ClientBaseError:
        return None
