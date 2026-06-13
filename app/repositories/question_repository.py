from __future__ import annotations

from pathlib import Path

from app.database.connection import get_connection
from app.database.models import Answer, Question


class QuestionRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    async def count_questions(self) -> int:
        async with get_connection(self.db_path) as connection:
            cursor = await connection.execute("SELECT COUNT(*) AS total FROM questions;")
            row = await cursor.fetchone()
            return int(row["total"])

    async def get_by_position(self, position: int) -> Question | None:
        async with get_connection(self.db_path) as connection:
            cursor = await connection.execute(
                "SELECT * FROM questions WHERE position = ?;",
                (position,),
            )
            question_row = await cursor.fetchone()
            if not question_row:
                return None

            cursor = await connection.execute(
                "SELECT * FROM answers WHERE question_id = ? ORDER BY position;",
                (question_row["id"],),
            )
            answers = [
                Answer(id=row["id"], question_id=row["question_id"], text=row["text"], position=row["position"])
                for row in await cursor.fetchall()
            ]
            return Question(
                id=question_row["id"],
                question_type=question_row["question_type"],
                text=question_row["text"],
                position=question_row["position"],
                answers=answers,
            )

    async def get_answer_score(self, answer_id: str) -> tuple[str, int] | None:
        async with get_connection(self.db_path) as connection:
            cursor = await connection.execute(
                """
                SELECT animal_id, score
                FROM answer_scores
                WHERE answer_id = ?
                ORDER BY id
                LIMIT 1;
                """,
                (answer_id,),
            )
            row = await cursor.fetchone()
            return (row["animal_id"], int(row["score"])) if row else None
