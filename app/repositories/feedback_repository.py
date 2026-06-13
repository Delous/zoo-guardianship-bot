from __future__ import annotations

from pathlib import Path

from app.database.connection import get_connection


class FeedbackRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    async def create_feedback(
        self,
        telegram_user_id: int,
        full_name: str,
        username: str | None,
        result_animal_id: str | None,
        rating: int,
        comment: str | None,
    ) -> None:
        async with get_connection(self.db_path) as connection:
            await connection.execute(
                """
                INSERT INTO feedback (
                    telegram_user_id, full_name, username, result_animal_id, rating, comment
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (telegram_user_id, full_name, username, result_animal_id, rating, comment),
            )
            await connection.commit()
