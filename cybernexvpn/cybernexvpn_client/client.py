from typing import Any

from aiogram.client.session import aiohttp

from cybernexvpn.cybernexvpn_client import schemas
from cybernexvpn.cybernexvpn_client.configuration import Configuration
from cybernexvpn.cybernexvpn_client.enums import MethodEnum

import logging

from cybernexvpn.cybernexvpn_client.errors import (
    NotFoundError,
    InvalidRequestDataError,
    ClientBaseError,
)
from cybernexvpn.cybernexvpn_client.schemas import CreatePaymentRequest

logging.basicConfig(level=logging.INFO)


class CyberNexVPNClient:

    def __init__(self):
        self._configuration = Configuration.instantiate()
        self._base_url = Configuration.api_url
        self._api_key = Configuration.api_key
        self._timeout = Configuration.timeout
        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def _handle_error(self, code: int, data: dict[str, Any] | None) -> None:
        if code == 404:
            raise NotFoundError()
        elif code == 400 and data and "error_message" in data:
            raise InvalidRequestDataError(data["error_message"])

        raise ClientBaseError()

    async def _make_request(self, request: schemas.Request, text=False):
        request.headers["x-api-key"] = self._api_key
        request_data = request.model_dump(by_alias=True)
        kwargs = {**request_data, "url": str(request.url)}

        request_data.pop("headers", None)

        async with self._session.request(timeout=self._timeout, **kwargs) as response:
            code = response.status
            logging.info(
                "Request: %s %s %s %s",
                request.method.value,
                request.url,
                code,
                request_data,
            )

            try:
                data = await response.text() if text else await response.json()
            except Exception:
                data = None

            try:
                response.raise_for_status()
                return data
            except Exception as e:
                logging.error("Error %s, error data: %s", e, data)
                await self._handle_error(code, data)

    # Servers

    async def get_servers(self) -> list[schemas.Server]:
        request = schemas.Request(
            url=f"{self._base_url}/servers/", method=MethodEnum.GET
        )
        response = await self._make_request(request)
        return [schemas.Server.model_validate(server) for server in response]

    # Users

    async def get_users(self) -> list[schemas.User]:
        request = schemas.Request(url=f"{self._base_url}/users/", method=MethodEnum.GET)
        response = await self._make_request(request)
        return [schemas.User.model_validate(user) for user in response]

    async def get_user(self, user_id: int) -> schemas.User:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/", method=MethodEnum.GET
        )
        data = await self._make_request(request)
        return schemas.User.model_validate(data)

    async def apply_invitation(
            self, user_id: int, request_schema: schemas.ApplyInvitationRequest
    ) -> None:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/apply-invitation/",
            json=request_schema.model_dump(),
        )
        await self._make_request(request)

    async def create_user(
            self, user_id: int, request_schema: schemas.CreateUserRequest
    ) -> schemas.User:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/",
            json=request_schema.model_dump(),
        )
        data = await self._make_request(request)
        return schemas.User.model_validate(data)

    ### Clients

    async def get_client(self, user_id: int, client_id: int) -> schemas.Client:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/",
            method=MethodEnum.GET,
        )
        data = await self._make_request(request)
        return schemas.Client.model_validate(data)

    async def get_clients(self, user_id: int) -> list[schemas.Client]:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/",
            method=MethodEnum.GET,
        )
        response = await self._make_request(request)
        return [schemas.Client.model_validate(client) for client in response]

    async def create_client(
            self, user_id: int, request_schema: schemas.CreateClientRequest
    ) -> schemas.Client:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/",
            method=MethodEnum.POST,
            json=request_schema.model_dump(),
        )
        data = await self._make_request(request)
        return schemas.Client.model_validate(data)

    async def patch_client(
            self, user_id: int, client_id: int, request_schema: schemas.PatchClientRequest
    ) -> schemas.Client:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/",
            method=MethodEnum.PATCH,
            json=request_schema.model_dump(exclude_unset=True),
        )
        data = await self._make_request(request)
        return schemas.Client.model_validate(data)

    async def delete_client(self, user_id: int, client_id: int):
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/",
            method=MethodEnum.DELETE,
        )
        await self._make_request(request)

    async def get_config_file(self, user_id: int, client_id: int) -> str:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/config/",
            method=MethodEnum.GET,
        )
        response = await self._make_request(request, text=True)
        return response

    async def reactivate_client(self, user_id: int, client_id: int) -> schemas.Client:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/reactivate/",
            method=MethodEnum.POST,
        )
        response = await self._make_request(request)
        return schemas.Client.model_validate(response)

    ### Payments

    async def create_payment(
            self, user_id: int, request_schema: CreatePaymentRequest
    ) -> schemas.PaymentUrl:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/payments/",
            method=MethodEnum.POST,
            json=request_schema.model_dump(),
        )
        response = await self._make_request(request)
        return schemas.PaymentUrl.model_validate(response)

    async def get_transaction_history(self, user_id: int):
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/payments/history/",
            method=MethodEnum.GET,
        )
        response = await self._make_request(request, text=True)
        return response

    ### Promo Codes

    async def apply_promo_code(
            self, user_id: int, request_schema: schemas.ApplyPromoCodeRequest
    ) -> schemas.ApplyPromoCodeResponse:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/apply-promo-code/",
            json=request_schema.model_dump(),
        )
        response = await self._make_request(request)
        return schemas.ApplyPromoCodeResponse.model_validate(response)
