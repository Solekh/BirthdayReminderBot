import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from db.model import Birthday
from conf import BOT_TOKEN, GROUP_ID
from bot.handlers import router  # Main bot handlers router
from bot.wether_handler import weather_router  # Weather-specific router

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Include both routers (handlers)
dp.include_router(router)
dp.include_router(weather_router)

# Configure logging
logging.basicConfig(level=logging.INFO)


async def check_birthdays():
    today = datetime.now().strftime("%m-%d")
    users = await Birthday().check_today_birthdays()
    for user in users:
        await bot.send_message(
            chat_id=GROUP_ID,
            text=f"Имрўз ҷигарбанди мо {user.name} зодрўз дорад. "
                 f"{user.name} дар санаи {user.birthdate} таваллуд шудааст. "
                 f"Аз номи хешу табор {user.name}ро бо зодрўзаш табрик мекунем!🥳🎂",
            parse_mode=ParseMode.HTML
        )


def setup_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_birthdays, 'cron', hour=5, minute=00)
    scheduler.start()


async def main():
    setup_scheduler()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
