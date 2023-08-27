from dispatcher import bot
from main import botDB

@bot.message_handler(commands="start")
async def start(message: types.Message):
    await message.bot.send_message(message.from_user.id, "hi")