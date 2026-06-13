from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.inline import completed_keyboard, continue_or_restart_keyboard, start_keyboard
from app.repositories.animal_repository import AnimalRepository
from app.services.quiz_service import QuizService


router = Router()


@router.message(CommandStart())
async def command_start(
    message: Message,
    state: FSMContext,
    animal_repository: AnimalRepository,
    quiz_service: QuizService,
) -> None:
    progress = await quiz_service.get_progress(message.from_user.id)
    start_text = await animal_repository.get_static_text("start")

    if progress and progress.finished_at:
        await message.answer(
            f"{start_text}\n\n{await animal_repository.get_static_text('completed_actions')}",
            reply_markup=completed_keyboard(),
        )
        return

    if progress and progress.selected_answers:
        await message.answer(
            f"{start_text}\n\n{await animal_repository.get_static_text('continue_or_restart')}",
            reply_markup=continue_or_restart_keyboard(),
        )
        return

    await state.clear()
    await message.answer(start_text, reply_markup=start_keyboard())
