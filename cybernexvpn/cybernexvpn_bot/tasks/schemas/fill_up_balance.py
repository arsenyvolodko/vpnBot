from pydantic import BaseModel


class FillUpBalance(BaseModel):
    user_id: int
    value: int
