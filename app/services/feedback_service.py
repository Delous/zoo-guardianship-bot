from __future__ import annotations

import logging

from aiogram.types import User

from app.database.models import Animal
from app.repositories.feedback_repository import FeedbackRepository


logger = logging.getLogger(__name__)


class FeedbackService:
    def __init__(self, feedback: FeedbackRepository) -> None:
        self.feedback = feedback

    async def save_feedback(
        self,
        user: User,
        animal: Animal | None,
        rating: int,
        comment: str | None,
    ) -> None:
        await self.feedback.create_feedback(
            telegram_user_id=user.id,
            full_name=user.full_name,
            username=user.username,
            result_animal_id=animal.id if animal else None,
            rating=rating,
            comment=comment,
        )
        logger.info("Feedback saved for user_id=%s rating=%s", user.id, rating)
