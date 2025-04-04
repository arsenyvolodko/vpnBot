import typing as tp
from typing import Any

from aiogram.client.session import aiohttp
from pydantic import BaseModel

from cybernexvpn.cybernexvpn_bot.bot.utils import new_text_storage
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

T = tp.TypeVar("T", bound=BaseModel)


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

    @staticmethod
    def validate_model(model: type[T], data: dict[str, Any]) -> T:
        try:
            return model.model_validate(data)
        except Exception as e:
            logging.error("Error due model validation: %s, error data: %s", e, data)
            raise ClientBaseError()

    async def _make_request(self, request: schemas.Request, text=False) -> str | dict[str, Any] | list[dict[str, Any]]:
        try:
            request.headers["X-API-KEY"] = self._api_key
            request_data = request.model_dump(by_alias=True)
            kwargs = {**request_data, "url": str(request.url)}

            request_data.pop("headers", None)

            code, data = None, None
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
        try:
            response = await self._make_request(request)
            return [self.validate_model(schemas.Server, server) for server in response]
        except NotFoundError:
            raise NotFoundError(new_text_storage.SERVER_NOT_FOUND_ERROR_MSG)

    async def get_server(self, server_id: int) -> schemas.Server:
        request = schemas.Request(
            url=f"{self._base_url}/servers/{server_id}/", method=MethodEnum.GET
        )
        try:
            server = await self._make_request(request)
            return self.validate_model(schemas.Server, server)
        except NotFoundError:
            raise NotFoundError(new_text_storage.SERVER_NOT_FOUND_ERROR_MSG)

    # Users

    async def get_users(self) -> list[schemas.User]:
        request = schemas.Request(url=f"{self._base_url}/users/", method=MethodEnum.GET)
        response = await self._make_request(request)
        return [self.validate_model(schemas.User, user) for user in response]

    async def get_user(self, user_id: int) -> schemas.User:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/", method=MethodEnum.GET
        )
        try:
            user = await self._make_request(request)
            return self.validate_model(schemas.User, user)
        except NotFoundError:
            raise NotFoundError(new_text_storage.USER_NOT_FOUND_ERROR_MSG)

    async def apply_invitation(
            self, user_id: int, request_schema: schemas.ApplyInvitationRequest
    ) -> None:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/apply-invitation/",
            json=request_schema.model_dump(),
        )
        try:
            await self._make_request(request)
        except NotFoundError:
            raise NotFoundError(new_text_storage.USER_NOT_FOUND_ERROR_MSG)

    async def create_user(
            self, user_id: int, request_schema: schemas.CreateUserRequest
    ) -> schemas.User:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/",
            json=request_schema.model_dump(),
        )
        user = await self._make_request(request)
        return self.validate_model(schemas.User, user)

    ### Clients

    async def get_client(self, user_id: int, client_id: int) -> schemas.Client:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/",
            method=MethodEnum.GET,
        )
        try:
            client = await self._make_request(request)
            return self.validate_model(schemas.Client, client)
        except NotFoundError:
            raise NotFoundError(new_text_storage.CLIENT_NOT_FOUND_ERROR_MSG)

    async def get_clients(self, user_id: int) -> list[schemas.Client]:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/",
            method=MethodEnum.GET,
        )
        try:
            clients = await self._make_request(request)
            return [self.validate_model(schemas.Client, client) for client in clients]
        except NotFoundError:
            raise NotFoundError(new_text_storage.USER_NOT_FOUND_ERROR_MSG)

    async def create_client(
            self, user_id: int, request_schema: schemas.CreateClientRequest
    ) -> schemas.Client:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/",
            method=MethodEnum.POST,
            json=request_schema.model_dump(),
        )
        try:
            client = await self._make_request(request)
            return self.validate_model(schemas.Client, client)
        except NotFoundError:
            raise NotFoundError(new_text_storage.USER_NOT_FOUND_ERROR_MSG)

    async def patch_client(
            self, user_id: int, client_id: int, request_schema: schemas.PatchClientRequest
    ) -> schemas.Client:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/",
            method=MethodEnum.PATCH,
            json=request_schema.model_dump(exclude_unset=True),
        )
        try:
            client = await self._make_request(request)
            return self.validate_model(schemas.Client, client)
        except NotFoundError:
            raise NotFoundError(new_text_storage.CLIENT_NOT_FOUND_ERROR_MSG)

    async def delete_client(self, user_id: int, client_id: int):
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/",
            method=MethodEnum.DELETE,
        )
        try:
            await self._make_request(request)
        except NotFoundError:
            raise NotFoundError(new_text_storage.CLIENT_ALREADY_DELETED_ERROR_MSG)

    async def get_config_file(self, user_id: int, client_id: int) -> str:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/config/",
            method=MethodEnum.GET,
        )
        try:
            return await self._make_request(request, text=True)
        except NotFoundError:
            raise NotFoundError(new_text_storage.CLIENT_NOT_FOUND_ERROR_MSG)

    async def reactivate_client(self, user_id: int, client_id: int) -> schemas.Client:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/clients/{client_id}/reactivate/",
            method=MethodEnum.POST,
        )
        try:
            client = await self._make_request(request)
            return self.validate_model(schemas.Client, client)
        except NotFoundError:
            raise NotFoundError(new_text_storage.CLIENT_NOT_FOUND_ERROR_MSG)

    ### Payments

    async def create_payment(
            self, user_id: int, request_schema: CreatePaymentRequest
    ) -> schemas.PaymentUrl:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/payments/",
            method=MethodEnum.POST,
            json=request_schema.model_dump(),
        )
        try:
            payment = await self._make_request(request)
            return self.validate_model(schemas.PaymentUrl, payment)
        except NotFoundError:
            raise NotFoundError(new_text_storage.USER_NOT_FOUND_ERROR_MSG)

    async def get_transaction_history(self, user_id: int) -> str:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/payments/history/",
            method=MethodEnum.GET,
        )
        try:
            return await self._make_request(request, text=True)
        except NotFoundError:
            raise NotFoundError(new_text_storage.USER_NOT_FOUND_ERROR_MSG)

    ### Promo Codes

    async def apply_promo_code(
            self, user_id: int, request_schema: schemas.ApplyPromoCodeRequest
    ) -> schemas.ApplyPromoCodeResponse:
        request = schemas.Request(
            url=f"{self._base_url}/users/{user_id}/apply-promo-code/",
            json=request_schema.model_dump(),
        )
        try:
            response = await self._make_request(request)
            return self.validate_model(schemas.ApplyPromoCodeResponse, response)
        except NotFoundError:
            # if promo code is not found -> code is 400
            raise NotFoundError(new_text_storage.USER_NOT_FOUND_ERROR_MSG)
