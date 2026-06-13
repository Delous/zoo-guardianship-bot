from __future__ import annotations

from pathlib import Path
import json

from app.database.connection import get_connection
from app.database.models import QuizProgress


class UserRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    @staticmethod
    def _map(row) -> QuizProgress:
        return QuizProgress(
            telegram_user_id=row["telegram_user_id"],
            current_state=row["current_state"],
            current_question_position=row["current_question_position"],
            scores=json.loads(row["scores_json"] or "{}"),
            selected_answers=json.loads(row["selected_answers_json"] or "[]"),
            result_animal_id=row["result_animal_id"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
        )

    async def get_progress(self, telegram_user_id: int) -> QuizProgress | None:
        async with get_connection(self.db_path) as connection:
            cursor = await connection.execute(
                "SELECT * FROM user_quiz_progress WHERE telegram_user_id = ?;",
                (telegram_user_id,),
            )
            row = await cursor.fetchone()
            return self._map(row) if row else None

    async def create_new_progress(self, telegram_user_id: int, state: str) -> None:
        async with get_connection(self.db_path) as connection:
            await connection.execute(
                """
                INSERT INTO user_quiz_progress (
                    telegram_user_id, current_state, current_question_position, scores_json,
                    selected_answers_json, fsm_data_json, result_animal_id, started_at, finished_at, updated_at
                )
                VALUES (?, ?, 1, '{}', '[]', '{}', NULL, CURRENT_TIMESTAMP, NULL, CURRENT_TIMESTAMP)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    current_state = excluded.current_state,
                    current_question_position = 1,
                    scores_json = '{}',
                    selected_answers_json = '[]',
                    fsm_data_json = '{}',
                    result_animal_id = NULL,
                    started_at = CURRENT_TIMESTAMP,
                    finished_at = NULL,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (telegram_user_id, state),
            )
            await connection.commit()

    async def save_answer(
        self,
        telegram_user_id: int,
        answer_id: str,
        animal_id: str,
        score: int,
        next_position: int,
    ) -> None:
        progress = await self.get_progress(telegram_user_id)
        scores = progress.scores if progress else {}
        selected_answers = progress.selected_answers if progress else []
        scores[animal_id] = int(scores.get(animal_id, 0)) + score
        selected_answers.append(answer_id)

        async with get_connection(self.db_path) as connection:
            await connection.execute(
                """
                UPDATE user_quiz_progress
                SET current_question_position = ?,
                    scores_json = ?,
                    selected_answers_json = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE telegram_user_id = ?;
                """,
                (next_position, json.dumps(scores, ensure_ascii=False), json.dumps(selected_answers, ensure_ascii=False), telegram_user_id),
            )
            await connection.commit()

    async def complete_quiz(self, telegram_user_id: int, result_animal_id: str, state: str) -> None:
        async with get_connection(self.db_path) as connection:
            await connection.execute(
                """
                UPDATE user_quiz_progress
                SET result_animal_id = ?,
                    current_state = ?,
                    finished_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE telegram_user_id = ?;
                """,
                (result_animal_id, state, telegram_user_id),
            )
            await connection.commit()

    async def set_state(self, telegram_user_id: int, state: str | None) -> None:
        async with get_connection(self.db_path) as connection:
            await connection.execute(
                """
                INSERT INTO user_quiz_progress (telegram_user_id, current_state, current_question_position)
                VALUES (?, ?, 1)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    current_state = excluded.current_state,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (telegram_user_id, state),
            )
            await connection.commit()
