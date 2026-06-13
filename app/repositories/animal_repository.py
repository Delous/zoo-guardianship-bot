from __future__ import annotations

from pathlib import Path

from app.database.connection import get_connection
from app.database.models import Animal


class AnimalRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    @staticmethod
    def _map(row) -> Animal:
        return Animal(
            id=row["id"],
            name=row["name"],
            result_title=row["result_title"],
            description=row["description"],
            fact=row["fact"],
            strengths=row["strengths"],
            motto=row["motto"],
            guardianship_text=row["guardianship_text"],
            image_filename=row["image_filename"],
        )

    async def get_by_id(self, animal_id: str) -> Animal | None:
        async with get_connection(self.db_path) as connection:
            cursor = await connection.execute("SELECT * FROM animals WHERE id = ?;", (animal_id,))
            row = await cursor.fetchone()
            return self._map(row) if row else None

    async def list_all(self) -> list[Animal]:
        async with get_connection(self.db_path) as connection:
            cursor = await connection.execute("SELECT * FROM animals ORDER BY rowid;")
            rows = await cursor.fetchall()
            return [self._map(row) for row in rows]

    async def get_static_text(self, key: str) -> str:
        async with get_connection(self.db_path) as connection:
            cursor = await connection.execute("SELECT text FROM static_texts WHERE key = ?;", (key,))
            row = await cursor.fetchone()
            return row["text"] if row else ""
