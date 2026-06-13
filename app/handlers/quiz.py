from __future__ import annotations

from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import QuizStates
from app.database.models import Question
from app.keyboards.inline import question_keyboard
from app.repositories.animal_repository import AnimalRepository
from app.services.quiz_service import QuizService
from app.services.result_service import ResultService
from app.services.sharing_service import SharingService
from app.handlers.result import send_result


router = Router()


async def send_question(message: Message, question: Question, animal_repository: AnimalRepository) -> None:
    title = await animal_repository.get_static_text("quiz_title")
    answers_text = "\n".join(
        f"{answer.position}. {escape(answer.text)}"
        for answer in question.answers
    )
    await message.answer(
        f"{escape(title)}\n\n"
        f"Вопрос {question.position}\n"
        f"{escape(question.text)}\n\n"
        f"{answers_text}",
        reply_markup=question_keyboard(question.answers),
    )


@router.callback_query(F.data == "quiz:start")
async def start_quiz(
    callback: CallbackQuery,
    state: FSMContext,
    quiz_service: QuizService,
    animal_repository: AnimalRepository,
) -> None:
    await state.set_state(QuizStates.answering)
    question = await quiz_service.start_new_quiz(callback.from_user.id, QuizStates.answering.state)
    intro = await animal_repository.get_static_text("before_questions")
    await callback.message.answer(intro)
    await send_question(callback.message, question, animal_repository)
    await callback.answer()


@router.callback_query(F.data == "quiz:continue")
async def continue_quiz(
    callback: CallbackQuery,
    state: FSMContext,
    quiz_service: QuizService,
    animal_repository: AnimalRepository,
) -> None:
    question = await quiz_service.get_current_question(callback.from_user.id)
    if question is None:
        await state.set_state(QuizStates.completed)
        await callback.message.answer(await animal_repository.get_static_text("completed_actions"))
    else:
        await state.set_state(QuizStates.answering)
        await send_question(callback.message, question, animal_repository)
    await callback.answer()


@router.callback_query(F.data == "quiz:restart")
async def restart_quiz(
    callback: CallbackQuery,
    state: FSMContext,
    quiz_service: QuizService,
    animal_repository: AnimalRepository,
) -> None:
    await state.set_state(QuizStates.answering)
    question = await quiz_service.start_new_quiz(callback.from_user.id, QuizStates.answering.state)
    await callback.message.answer(await animal_repository.get_static_text("restart"))
    await send_question(callback.message, question, animal_repository)
    await callback.answer()


@router.callback_query(QuizStates.answering, F.data.startswith("quiz:answer:"))
async def accept_answer(
    callback: CallbackQuery,
    state: FSMContext,
    quiz_service: QuizService,
    result_service: ResultService,
    sharing_service: SharingService,
    animal_repository: AnimalRepository,
) -> None:
    answer_id = callback.data.split(":", maxsplit=2)[2]
    finished = await quiz_service.accept_answer(callback.from_user.id, answer_id)

    if finished:
        await state.set_state(QuizStates.completed)
        await callback.message.answer(await animal_repository.get_static_text("before_result"))
        animal = await result_service.get_or_create_result(callback.from_user.id, QuizStates.completed.state)
        await send_result(callback.message, animal, result_service, sharing_service)
    else:
        question = await quiz_service.get_current_question(callback.from_user.id)
        if question:
            await send_question(callback.message, question, animal_repository)

    await callback.answer()
