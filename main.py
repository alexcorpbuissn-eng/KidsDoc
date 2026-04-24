"""
Local development entry point.
Use this file to run the bot locally via polling (python main.py).
On PythonAnywhere, the bot runs through webhooks inside app.py instead.
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import config
import database as db
from handlers import router

logging.basicConfig(level=logging.INFO)

async def main():
    await db.init_db()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    print("Bot is starting (polling mode)...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
