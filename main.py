import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_ID
from handlers_user import router as user_router
from handlers_admin import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set! Please add it to .env")
        return
    if not ADMIN_ID:
        logger.error("ADMIN_ID is not set! Please add it to .env")
        return

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(user_router)

    me = await bot.get_me()
    logger.info(f"Bot started: @{me.username} (ID: {me.id})")
    logger.info(f"Admin ID: {ADMIN_ID}")

    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
