from __future__ import annotations

from pathlib import Path
import json

import aiosqlite
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    async def _connect(self) -> aiosqlite.Connection:
        connection = await aiosqlite.connect(self.db_path)
        connection.row_factory = aiosqlite.Row
        await connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    @staticmethod
    def _user_id(key: StorageKey) -> int:
        return int(key.user_id or key.chat_id)

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        state_value = state.state if isinstance(state, State) else state
        connection = await self._connect()
        try:
            await connection.execute(
                """
                INSERT INTO user_quiz_progress (telegram_user_id, current_state, current_question_position)
                VALUES (?, ?, 1)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    current_state = excluded.current_state,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (self._user_id(key), state_value),
            )
            await connection.commit()
        finally:
            await connection.close()

    async def get_state(self, key: StorageKey) -> str | None:
        connection = await self._connect()
        try:
            cursor = await connection.execute(
                "SELECT current_state FROM user_quiz_progress WHERE telegram_user_id = ?;",
                (self._user_id(key),),
            )
            row = await cursor.fetchone()
            return row["current_state"] if row else None
        finally:
            await connection.close()

    async def set_data(self, key: StorageKey, data: dict) -> None:
        connection = await self._connect()
        try:
            await connection.execute(
                """
                INSERT INTO user_quiz_progress (telegram_user_id, current_question_position, fsm_data_json)
                VALUES (?, 1, ?)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    fsm_data_json = excluded.fsm_data_json,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (self._user_id(key), json.dumps(data, ensure_ascii=False)),
            )
            await connection.commit()
        finally:
            await connection.close()

    async def get_data(self, key: StorageKey) -> dict:
        connection = await self._connect()
        try:
            cursor = await connection.execute(
                "SELECT fsm_data_json FROM user_quiz_progress WHERE telegram_user_id = ?;",
                (self._user_id(key),),
            )
            row = await cursor.fetchone()
            return json.loads(row["fsm_data_json"] or "{}") if row else {}
        finally:
            await connection.close()

    async def update_data(self, key: StorageKey, data: dict) -> dict:
        current = await self.get_data(key)
        current.update(data)
        await self.set_data(key, current)
        return current

    async def close(self) -> None:
        return None
