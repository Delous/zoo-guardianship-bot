from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import ContactStates, QuizStates
from app.keyboards.inline import completed_keyboard, result_keyboard
from app.repositories.animal_repository import AnimalRepository
from app.services.contact_service import ContactService
from app.services.quiz_service import QuizService
from app.services.sharing_service import SharingService


router = Router()


@router.callback_query(F.data == "contact:start")
async def contact_start(callback: CallbackQuery, state: FSMContext, animal_repository: AnimalRepository) -> None:
    await state.set_state(ContactStates.waiting_question)
    await callback.message.answer(await animal_repository.get_static_text("contact_intro"))
    await callback.answer()


@router.message(ContactStates.waiting_question, F.text)
async def contact_question(
    message: Message,
    state: FSMContext,
    contact_service: ContactService,
    quiz_service: QuizService,
    sharing_service: SharingService,
    animal_repository: AnimalRepository,
) -> None:
    progress = await quiz_service.get_progress(message.from_user.id)
    animal = await animal_repository.get_by_id(progress.result_animal_id) if progress and progress.result_animal_id else None
    notified = await contact_service.save_and_notify(message.bot, message.from_user, animal, message.text)
    await state.set_state(QuizStates.completed)
    if animal:
        reply_markup = result_keyboard(await sharing_service.build_share_url(animal))
    else:
        reply_markup = completed_keyboard()

    if notified:
        text = await animal_repository.get_static_text("contact_success")
    else:
        text = (
            "Спасибо! Ваш вопрос сохранён, но сейчас не удалось отправить уведомление сотруднику. "
            "Мы сможем найти обращение в базе."
        )

    await message.answer(text, reply_markup=reply_markup)
