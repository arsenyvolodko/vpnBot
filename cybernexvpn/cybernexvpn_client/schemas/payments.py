from pydantic import BaseModel


class CreatePaymentRequest(BaseModel):
    value: int


class PaymentUrl(BaseModel):
    url: str
