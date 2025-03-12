from pydantic import BaseModel


class ApplyPromoCodeRequest(BaseModel):
    code: str


class ApplyPromoCodeResponse(BaseModel):
    value: int
