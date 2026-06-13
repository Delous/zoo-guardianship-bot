from __future__ import annotations

import logging

from app.database.models import Question, QuizProgress
from app.repositories.question_repository import QuestionRepository
from app.repositories.user_repository import UserRepository


logger = logging.getLogger(__name__)


class QuizService:
    def __init__(self, questions: QuestionRepository, users: UserRepository) -> None:
        self.questions = questions
        self.users = users

    async def get_progress(self, telegram_user_id: int) -> QuizProgress | None:
        return await self.users.get_progress(telegram_user_id)

    async def start_new_quiz(self, telegram_user_id: int, state: str) -> Question:
        await self.users.create_new_progress(telegram_user_id, state)
        logger.info("Quiz started for user_id=%s", telegram_user_id)
        question = await self.questions.get_by_position(1)
        if question is None:
            raise RuntimeError("Quiz has no questions")
        return question

    async def get_current_question(self, telegram_user_id: int) -> Question | None:
        progress = await self.users.get_progress(telegram_user_id)
        if not progress or progress.finished_at:
            return None
        return await self.questions.get_by_position(progress.current_question_position)

    async def accept_answer(self, telegram_user_id: int, answer_id: str) -> bool:
        progress = await self.users.get_progress(telegram_user_id)
        if not progress or progress.finished_at:
            return False

        score = await self.questions.get_answer_score(answer_id)
        if score is None:
            return False

        total_questions = await self.questions.count_questions()
        next_position = progress.current_question_position + 1
        await self.users.save_answer(telegram_user_id, answer_id, score[0], score[1], next_position)
        return next_position > total_questions
