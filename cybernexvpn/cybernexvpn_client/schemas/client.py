import datetime
from typing import Optional

from pydantic import BaseModel

from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.enums import ClientTypeEnum


class Client(BaseModel):
    id: int
    name: str
    is_active: bool
    end_date: datetime.date
    server: schemas.Server
    price: int
    auto_renew: bool = True
    type: ClientTypeEnum


class CreateClientRequest(BaseModel):
    server_id: int
    type: ClientTypeEnum


class PatchClientRequest(BaseModel):
    name: Optional[str] = None
    auto_renew: Optional[bool] = None
    type: Optional[ClientTypeEnum] = None
