from fastapi import FastAPI

from fastapi import Request
from celery_config import celery_app

app = FastAPI()


@app.post("/api/v1/payment_succeeded/", status_code=200)
async def search_track(request: Request):
    payment_json = await request.json()
    celery_app.send_task("vpnBot.celery_tasks.process_payment", args=[payment_json])
