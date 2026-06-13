from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_chat_id: int
    bot_username: str
    database_path: Path

    @property
    def bot_link(self) -> str:
        return f"https://t.me/{self.bot_username.lstrip('@')}"


def load_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env")

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_chat_id = os.getenv("ADMIN_CHAT_ID", "").strip()
    bot_username = os.getenv("BOT_USERNAME", "").strip()
    database_path = os.getenv("DATABASE_PATH", "zoo_guardianship_bot.db").strip()

    if not bot_token:
        raise RuntimeError("BOT_TOKEN is required in .env")
    if not admin_chat_id:
        raise RuntimeError("ADMIN_CHAT_ID is required in .env")
    if not bot_username:
        raise RuntimeError("BOT_USERNAME is required in .env")

    db_path = Path(database_path)
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path

    return Settings(
        bot_token=bot_token,
        admin_chat_id=int(admin_chat_id),
        bot_username=bot_username,
        database_path=db_path,
    )
