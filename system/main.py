from aiogram import executor
from dispatcher import bot
from db import BotDB
import os
# from background import keep_alive
from dispatcher import bot
from handlers import actions

# не стирать никакие импорты!!!!

botDB = BotDB()
# keep_alive()

if __name__ == "__main__":
    executor.start_polling(bot, skip_updates=True)
