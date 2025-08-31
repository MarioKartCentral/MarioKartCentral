"""
Database wrapper providing unified access to SQLite and DuckDB.
"""

from dataclasses import dataclass
import logging
import sqlite3
import aiosqlite
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class DBWrapperConnection():
    connection: aiosqlite.Connection
    readonly: bool
    attach: Dict[str, str]
    autocommit: bool
    foreign_keys: bool = True

    async def __aenter__(self) -> aiosqlite.Connection:
        db = await self.connection
        if not self.readonly:
            if self.foreign_keys:
                await db.execute("pragma foreign_keys = ON;")
            await db.execute("pragma synchronous = NORMAL;")
            await db.execute("PRAGMA busy_timeout = 5000")
        for name, path in self.attach.items():
            await db.execute(f"ATTACH DATABASE :path AS :name", {"path": path, "name": name})

        def set_autocommit(new_autocommit_value: bool):
            self.connection._conn.autocommit = new_autocommit_value # pyright: ignore[reportPrivateUsage]

        await self.connection._execute(set_autocommit, self.autocommit) # pyright: ignore[reportPrivateUsage]
        return db

    async def __aexit__(self, *_: Any) -> None:
        await self.connection.close()


@dataclass
class DBWrapper():
    db_paths: Dict[str, str]

    def reset_db(self, db_name: str = 'main'):
        """Resets the specified database file. Defaults to 'main'."""
        path = self.db_paths.get(db_name)
        if path:
            logging.info(f"Resetting database file: {path}")
            open(path, 'w').close()
        else:
            raise ValueError(f"Database '{db_name}' not configured for reset.")

    def connect(self, db_name: str = 'main', attach: List[str] = [], readonly: bool = False, autocommit: bool = False, foreign_keys: bool = True):
        """Connects to the specified database."""
        path = self.db_paths.get(db_name)
        if not path:
            raise ValueError(f"Database '{db_name}' not configured.")

        attach_dict: Dict[str, str] = {}
        for db in attach:
            if db not in self.db_paths:
                raise ValueError(f"Database '{db}' not configured.")
            attach_dict[db] = self.db_paths[db]

        if readonly:
            path = f"file:{path}?mode=ro"
            for db in attach_dict:
                attach_dict[db] = f"file:{attach_dict[db]}?mode=ro"

        def connector() -> sqlite3.Connection:
            conn = sqlite3.connect(path, autocommit=True) # Connection is created with autocommit=True, but it is disabled later
            conn.setlimit(sqlite3.SQLITE_LIMIT_ATTACHED, len(attach_dict)) # Limit the number of attached dbs as a security measure
            return conn

        db_connection = aiosqlite.Connection(connector, iter_chunk_size=64)
        return DBWrapperConnection(db_connection, readonly, attach_dict, autocommit, foreign_keys=foreign_keys)
