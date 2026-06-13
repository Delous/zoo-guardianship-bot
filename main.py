from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.dispatcher import build_dispatcher
from app.config import load_settings
from app.database.connection import init_database


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


async def main() -> None:
    setup_logging()
    settings = load_settings()
    init_database(settings.database_path)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher(settings)

    logging.getLogger(__name__).info("Bot polling started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
