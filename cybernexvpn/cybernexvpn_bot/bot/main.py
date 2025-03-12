import asyncio
import logging
import sys

from aiogram import Bot

from cybernexvpn.cybernexvpn_bot.config import BOT_TOKEN


async def main() -> None:
    from cybernexvpn.cybernexvpn_bot.bot.bot import dp
    await dp.start_polling(bot)


bot = Bot(token=BOT_TOKEN)
loop = asyncio.new_event_loop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop.run_until_complete(main())
