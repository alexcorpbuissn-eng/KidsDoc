import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
import config
import database as db
from handlers import router

logging.basicConfig(level=logging.INFO)

async def main():
    await db.init_db()
    
    # Use proxy if running on PythonAnywhere
    if os.path.exists("/home/KidsDoc"):
        session = AiohttpSession(proxy="http://proxy.server:3128")
        bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
    else:
        bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        
    dp = Dispatcher()
    
    dp.include_router(router)
    
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
