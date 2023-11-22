from aiogram import executor
from shared import bot
from handlers import actions  # do not clear


if __name__ == "__main__":
    executor.start_polling(bot, skip_updates=True)
