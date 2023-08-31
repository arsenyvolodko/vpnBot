from aiogram import executor
from system.dispatcher import bot
from db import BotDB
import os
from handlers import actions
# from system.background import keep_alive

# не стирать никакие импорты!!!!

botDB = BotDB()
# keep_alive()

if __name__ == "__main__":
    executor.start_polling(bot, skip_updates=True)
