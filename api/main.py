from fastapi import FastAPI, Header, Request

from api import schemas
from api.utils import _check_api_key
from cybernexvpn.cybernexvpn_bot.core.celery import app as celery_app


app = FastAPI()


@app.post("/api/v1/succeed-payment/{user_id}/{payment_id}", status_code=200)
async def handle_payment_succeeded(
    request: Request, user_id: int, payment_id: str, x_api_key: str = Header(None)
):
    _check_api_key(x_api_key)
    celery_app.send_task(
        "cybernexvpn.cybernexvpn_bot.tasks.tasks.handle_payment_succeeded",
        args=[user_id, payment_id],
    )


@app.post("/api/v1/send-message/", status_code=200)
async def send_message_from_admin(
    message: schemas.Message, x_api_key: str = Header(None)
):
    _check_api_key(x_api_key)
    celery_app.send_task(
        "cybernexvpn.cybernexvpn_bot.tasks.tasks.send_message_from_admin",
        args=[message.model_dump()],
    )


@app.post("/api/v1/make-subscription-updates/", status_code=200)
async def make_subscription_updates(
    updates: schemas.SubscriptionUpdates, x_api_key: str = Header(None)
):
    _check_api_key(x_api_key)
    celery_app.send_task(
        "cybernexvpn.cybernexvpn_bot.tasks.tasks.make_subscription_updates",
        args=[updates.model_dump()],
    )
