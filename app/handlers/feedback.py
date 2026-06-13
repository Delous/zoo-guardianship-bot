from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

from app.bot.states import FeedbackStates, QuizStates
from app.keyboards.inline import completed_keyboard, feedback_rating_keyboard, feedback_skip_keyboard, result_keyboard
from app.repositories.animal_repository import AnimalRepository
from app.services.feedback_service import FeedbackService
from app.services.quiz_service import QuizService
from app.services.sharing_service import SharingService


router = Router()


@router.callback_query(F.data == "feedback:start")
async def feedback_start(callback: CallbackQuery, state: FSMContext, animal_repository: AnimalRepository) -> None:
    await state.set_state(FeedbackStates.waiting_rating)
    await callback.message.answer(
        await animal_repository.get_static_text("feedback_intro"),
        reply_markup=feedback_rating_keyboard(),
    )
    await callback.answer()


@router.callback_query(FeedbackStates.waiting_rating, F.data.startswith("feedback:rating:"))
async def feedback_rating(callback: CallbackQuery, state: FSMContext, animal_repository: AnimalRepository) -> None:
    rating = int(callback.data.rsplit(":", maxsplit=1)[1])
    await state.update_data(feedback_rating=rating)
    await state.set_state(FeedbackStates.waiting_comment)
    await callback.message.answer(
        await animal_repository.get_static_text("feedback_comment_request"),
        reply_markup=feedback_skip_keyboard(await animal_repository.get_static_text("no_comment")),
    )
    await callback.answer()


async def _save_feedback(
    message: Message,
    user: User,
    state: FSMContext,
    comment: str | None,
    feedback_service: FeedbackService,
    quiz_service: QuizService,
    sharing_service: SharingService,
    animal_repository: AnimalRepository,
) -> None:
    data = await state.get_data()
    rating = int(data.get("feedback_rating", 0))
    progress = await quiz_service.get_progress(user.id)
    animal = await animal_repository.get_by_id(progress.result_animal_id) if progress and progress.result_animal_id else None
    await feedback_service.save_feedback(user, animal, rating, comment)
    await state.set_state(QuizStates.completed)
    if animal:
        reply_markup = result_keyboard(await sharing_service.build_share_url(animal))
    else:
        reply_markup = completed_keyboard()
    await message.answer(await animal_repository.get_static_text("feedback_success"), reply_markup=reply_markup)


@router.message(FeedbackStates.waiting_comment, F.text)
async def feedback_comment(
    message: Message,
    state: FSMContext,
    feedback_service: FeedbackService,
    quiz_service: QuizService,
    sharing_service: SharingService,
    animal_repository: AnimalRepository,
) -> None:
    await _save_feedback(
        message,
        message.from_user,
        state,
        message.text,
        feedback_service,
        quiz_service,
        sharing_service,
        animal_repository,
    )


@router.callback_query(FeedbackStates.waiting_comment, F.data == "feedback:skip")
async def feedback_skip(
    callback: CallbackQuery,
    state: FSMContext,
    feedback_service: FeedbackService,
    quiz_service: QuizService,
    sharing_service: SharingService,
    animal_repository: AnimalRepository,
) -> None:
    await _save_feedback(
        callback.message,
        callback.from_user,
        state,
        None,
        feedback_service,
        quiz_service,
        sharing_service,
        animal_repository,
    )
    await callback.answer()
