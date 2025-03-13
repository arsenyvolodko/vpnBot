from pydantic import BaseModel


class PaymentModel(BaseModel):
    user_id: int
    message_id: int
    value: int
