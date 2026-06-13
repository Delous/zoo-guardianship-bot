from __future__ import annotations

import logging
from pathlib import Path

from app.database.models import Animal
from app.repositories.animal_repository import AnimalRepository
from app.repositories.user_repository import UserRepository


logger = logging.getLogger(__name__)


class ResultService:
    def __init__(self, animals: AnimalRepository, users: UserRepository, media_dir: Path) -> None:
        self.animals = animals
        self.users = users
        self.media_dir = media_dir

    async def get_or_create_result(self, telegram_user_id: int, completed_state: str) -> Animal:
        progress = await self.users.get_progress(telegram_user_id)
        if not progress:
            raise RuntimeError("Cannot build result without quiz progress")

        if progress.result_animal_id:
            animal = await self.animals.get_by_id(progress.result_animal_id)
            if animal:
                return animal

        all_animals = await self.animals.list_all()
        scores = progress.scores
        result = max(all_animals, key=lambda animal: (scores.get(animal.id, 0), -all_animals.index(animal)))
        await self.users.complete_quiz(telegram_user_id, result.id, completed_state)
        logger.info("Quiz completed for user_id=%s result=%s", telegram_user_id, result.id)
        return result

    def image_path_for(self, animal: Animal) -> Path:
        return self.media_dir / animal.image_filename

    async def format_result_text(self, animal: Animal) -> str:
        return (
            f"{animal.result_title}\n\n"
            f"{animal.description}\n\n"
            f"Факт: {animal.fact}\n\n"
            f"Сильные стороны: {animal.strengths}\n"
            f"Девиз: {animal.motto}\n\n"
            f"Опека: {animal.guardianship_text}"
        )

    async def guardianship_text(self) -> str:
        return await self.animals.get_static_text("guardianship_full")
