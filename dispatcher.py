import logging
from aiogram import Bot, Dispatcher
import config

logging.basicConfig(level=logging.INFO)

if not config.TOKEN:
    exit("No token provided")

pre_bot = Bot(token=config.TOKEN, parse_mode="HTML")
bot = Dispatcher(pre_bot)
