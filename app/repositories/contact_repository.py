from __future__ import annotations

from pathlib import Path

from app.database.connection import get_connection


class ContactRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    async def create_request(
        self,
        telegram_user_id: int,
        full_name: str,
        username: str | None,
        result_animal_id: str | None,
        question_text: str,
    ) -> str:
        async with get_connection(self.db_path) as connection:
            cursor = await connection.execute(
                """
                INSERT INTO contact_requests (
                    telegram_user_id, full_name, username, result_animal_id, question_text
                )
                VALUES (?, ?, ?, ?, ?)
                RETURNING created_at;
                """,
                (telegram_user_id, full_name, username, result_animal_id, question_text),
            )
            row = await cursor.fetchone()
            await connection.commit()
            return row["created_at"]
