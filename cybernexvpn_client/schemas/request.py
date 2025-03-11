from typing import Any

from pydantic import BaseModel, HttpUrl, Field, ConfigDict

from cybernexvpn_client.enums import MethodEnum


class Request(BaseModel):
    url: HttpUrl | str
    method: MethodEnum = MethodEnum.POST
    headers: dict[str, Any] = Field(default_factory=dict)

    params: dict[str, Any] | None = None
    data: dict[str, Any] | None = None
    json_: dict[str, Any] | None = Field(None, alias="json")

    model_config = ConfigDict(arbitrary_types_allowed=True)
