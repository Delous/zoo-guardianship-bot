from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.services.result_service import ResultService


router = Router()


@router.callback_query(F.data == "guardianship:more")
async def guardianship_more(callback: CallbackQuery, result_service: ResultService) -> None:
    await callback.message.answer(await result_service.guardianship_text())
    await callback.answer()
