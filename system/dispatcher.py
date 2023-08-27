import logging
from aiogram import Bot, Dispatcher
import system.config

# Configure logging
logging.basicConfig(level=logging.INFO)

# prerequisites
if not system.config.TOKEN:
    exit("No token provided")

# init
pre_bot = Bot(token=system.config.TOKEN, parse_mode="HTML")
bot = Dispatcher(pre_bot)
