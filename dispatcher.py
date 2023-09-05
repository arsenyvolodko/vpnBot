import logging
from aiogram import Bot, Dispatcher
import config

# Configure logging
logging.basicConfig(level=logging.INFO)

# prerequisites
if not config.TOKEN:
    exit("No token provided")

# init
pre_bot = Bot(token=config.TOKEN, parse_mode="HTML")
bot = Dispatcher(pre_bot)
