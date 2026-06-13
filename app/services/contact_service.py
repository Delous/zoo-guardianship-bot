from __future__ import annotations

import logging

from aiogram import Bot
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
    ) -> None:
        created_at = await self.contacts.create_request(
            telegram_user_id=user.id,
            full_name=user.full_name,
            username=user.username,
            result_animal_id=animal.id if animal else None,
            question_text=question_text,
        )
        username = f"@{user.username}" if user.username else "не указан"
        animal_name = animal.name if animal else "результат ещё не получен"
        await bot.send_message(
            self.admin_chat_id,
            "Новое обращение по программе опеки\n\n"
            f"Пользователь: {user.full_name}\n"
            f"Username: {username}\n"
            f"Telegram ID: {user.id}\n"
            f"Итоговое животное: {animal_name}\n"
            f"Дата обращения: {created_at}\n\n"
            f"Вопрос:\n{question_text}",
        )
        logger.info("Contact request sent to admin for user_id=%s", user.id)
