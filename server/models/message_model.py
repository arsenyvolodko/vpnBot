from pydantic import BaseModel


class MessageModel(BaseModel):
    text: str
    only_to_me: bool
