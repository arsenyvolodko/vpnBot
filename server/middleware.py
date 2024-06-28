from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

ALLOWED_IPS = {
    "127.0.0.1",
    "localhost",
    "185.71.76.0",
    "185.71.76.0/27",
    "185.71.77.0",
    "185.71.77.0/27",
    "77.75.153.0",
    "77.75.153.0/25",
    "77.75.156.11",
    "77.75.156.35",
    "77.75.154.128",
    "77.75.154.128/25",
    "2a02:5180::/32",
}


class IPFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        if client_ip not in ALLOWED_IPS:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: Your IP address is not allowed.",
            )
        response = await call_next(request)
        return response
