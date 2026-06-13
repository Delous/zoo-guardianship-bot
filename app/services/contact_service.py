from __future__ import annotations

import logging
from html import escape

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import User

from app.database.models import Animal
from app.repositories.contact_repository import ContactRepository


logger = logging.getLogger(__name__)


class ContactService:
    def __init__(self, contacts: ContactRepository, admin_chat_id: int) -> None:
        self.contacts = contacts
        self.admin_chat_id = admin_chat_id

    async def save_and_notify(
        self,
        bot: Bot,
        user: User,
        animal: Animal | None,
        question_text: str,
    ) -> bool:
        created_at = await self.contacts.create_request(
            telegram_user_id=user.id,
            full_name=user.full_name,
            username=user.username,
            result_animal_id=animal.id if animal else None,
            question_text=question_text,
        )
        username = f"@{user.username}" if user.username else "не указан"
        animal_name = animal.name if animal else "результат ещё не получен"
        try:
            await bot.send_message(
                self.admin_chat_id,
                "Новое обращение по программе опеки\n\n"
                f"Пользователь: {escape(user.full_name)}\n"
                f"Username: {escape(username)}\n"
                f"Telegram ID: {user.id}\n"
                f"Итоговое животное: {escape(animal_name)}\n"
                f"Дата обращения: {escape(created_at)}\n\n"
                f"Вопрос:\n{escape(question_text)}",
            )
        except TelegramAPIError:
            logger.exception("Could not send contact request to admin_chat_id=%s", self.admin_chat_id)
            return False

        logger.info("Contact request sent to admin for user_id=%s", user.id)
        return True
