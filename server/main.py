from fastapi import FastAPI, Request

from celery_config import celery_app
from server.middleware import IPFilterMiddleware
from server.models.message_model import MessageModel

app = FastAPI()

app.add_middleware(IPFilterMiddleware)


@app.post("/api/v1/payment_succeeded/", status_code=200)
async def search_track(request: Request):
    payment_json = await request.json()
    celery_app.send_task("vpnBot.celery_tasks.process_payment", args=[payment_json])


@app.post("/api/v1/send_message/", status_code=200)
async def send_message(message_model: MessageModel):
    celery_app.send_task(
        "vpnBot.celery_tasks.send_message_to_everyone", args=[message_model.dict()]
    )
