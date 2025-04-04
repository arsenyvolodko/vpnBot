from pydantic import BaseModel


class Server(BaseModel):
    id: int
    name: str
    price: int
    tag: str
