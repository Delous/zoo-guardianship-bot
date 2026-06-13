from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import logging
import sqlite3

import aiosqlite

from app.database.seed import create_tables, seed_database


logger = logging.getLogger(__name__)


def init_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        create_tables(connection)
        seed_database(connection)
    logger.info("SQLite database is ready: %s", db_path)


@asynccontextmanager
async def get_connection(db_path: Path):
    connection = await aiosqlite.connect(db_path)
    connection.row_factory = aiosqlite.Row
    await connection.execute("PRAGMA foreign_keys = ON;")
    try:
        yield connection
    finally:
        await connection.close()
