from pydantic import BaseModel


class Message(BaseModel):
    text: str
    only_to_me: bool
