from aiogram import executor
# from dispatcher import bot
# from db import BotDB
import os
from shared import bot, botDB
from handlers import actions
# from background import keep_alive

# не стирать никакие импорты!!!!


if __name__ == "__main__":
    executor.start_polling(bot, skip_updates=True)
