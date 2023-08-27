from system.dispatcher import bot
from system.main import botDB
from aiogram import types

@bot.message_handler(commands="start")
async def start(message: types.Message):
    await message.bot.send_message(message.from_user.id, "hi")