import datetime
from typing import Optional

from pydantic import BaseModel

from cybernexvpn_client.enums import ClientTypeEnum


class Client(BaseModel):
    id: int
    name: str
    is_active: bool
    end_date: datetime.date
    server_name: str
    price: int
    auto_renew: bool = True
    type: ClientTypeEnum


class CreateClientRequest(BaseModel):
    server: int
    type: ClientTypeEnum


class PatchClientRequest(BaseModel):
    name: Optional[str] = None
    auto_renew: Optional[bool] = None
    type: Optional[ClientTypeEnum] = None
