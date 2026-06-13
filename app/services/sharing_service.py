from __future__ import annotations

from urllib.parse import quote_plus

from app.database.models import Animal
from app.repositories.animal_repository import AnimalRepository


class SharingService:
    def __init__(self, animals: AnimalRepository, bot_link: str) -> None:
        self.animals = animals
        self.bot_link = bot_link

    async def build_share_url(self, animal: Animal) -> str:
        template = await self.animals.get_static_text("share_text_template")
        text = template.format(animal_name=animal.name)
        return f"https://t.me/share/url?url={quote_plus(self.bot_link)}&text={quote_plus(text)}"
