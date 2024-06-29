from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from vpnBot.config import ALLOWED_IPS

app = FastAPI()


class IPFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        if client_ip not in ALLOWED_IPS:
            return Response(content="Invalid IP", status_code=403)
        response = await call_next(request)
        return response
