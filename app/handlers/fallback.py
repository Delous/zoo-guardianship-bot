from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery, Message

from app.repositories.animal_repository import AnimalRepository


router = Router()


@router.callback_query()
async def unknown_callback(callback: CallbackQuery, animal_repository: AnimalRepository) -> None:
    await callback.message.answer(await animal_repository.get_static_text("fallback"))
    await callback.answer()


@router.message()
async def unknown_message(message: Message, animal_repository: AnimalRepository) -> None:
    await message.answer(await animal_repository.get_static_text("fallback"))
