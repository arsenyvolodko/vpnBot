from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):

    class Config:
        arbitrary_types_allowed = True


class Message(BaseModel):
    text: str
    only_to_me: bool = True


class SubscriptionUpdated(BaseModel):
    pass


class FillUpBalance(BaseModel):
    user_id: int
    value: int
