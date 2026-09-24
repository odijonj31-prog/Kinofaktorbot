import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db
from handlers import user, vip, admin, content_channel, ai_recommend

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Tartib muhim: admin va content_channel avval, keyin vip, oxirida user
    # (user routerida "har qanday matn"ni ushlab qoluvchi handler bor)
    dp.include_router(admin.router)
    dp.include_router(content_channel.router)
    dp.include_router(ai_recommend.router)
    dp.include_router(vip.router)
    dp.include_router(user.router)

    await init_db()
    print("✅ Baza tayyor, bot ishga tushmoqda...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
