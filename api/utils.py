from fastapi import HTTPException

from api.config import API_KEY


def _check_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403)
