import asyncio

from aiogram import Bot

from cybernexvpn.cybernexvpn_bot.config import BOT_TOKEN
from cybernexvpn.cybernexvpn_bot.logging_config import setup_logging

setup_logging()


async def main() -> None:
    from cybernexvpn.cybernexvpn_bot.bot.bot import dp

    await dp.start_polling(bot)


bot = Bot(token=BOT_TOKEN)
loop = asyncio.new_event_loop()


if __name__ == "__main__":
    loop.run_until_complete(main())
