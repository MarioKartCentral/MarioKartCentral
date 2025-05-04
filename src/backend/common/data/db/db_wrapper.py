from dataclasses import dataclass
from types import TracebackType
import aiosqlite
import sqlite3
from typing import Dict, List, Set


@dataclass
class DBWrapperConnection():
    connection: aiosqlite.Connection
    readonly: bool
    attach: Dict[str, str]

    async def __aenter__(self) -> aiosqlite.Connection:
        db = await self.connection
        if not self.readonly:
            await db.execute("pragma foreign_keys = ON;")
        for name, path in self.attach.items():
            # use string interpolation as otherwise the authorizer won't work
            await db.execute(f"ATTACH DATABASE '{path}' AS '{name}'")
        return db

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        await self.connection.close()


@dataclass
class DBWrapper():
    db_paths: Dict[str, str]

    def reset_db(self, db_name: str = 'main'):
        """Resets the specified database file. Defaults to 'main'."""
        path = self.db_paths.get(db_name)
        if path:
            print(f"Resetting database file: {path}")
            open(path, 'w').close()
        else:
            raise ValueError(f"Database '{db_name}' not configured for reset.")

    def connect(self, db_name: str = 'main', attach: List[str] = [], readonly=False, autocommit=False):
        """Connects to the specified database."""
        path = self.db_paths.get(db_name)
        if not path:
            raise ValueError(f"Database '{db_name}' not configured.")
        
        attach_dict: Dict[str, str] = {}
        allowed_dbs: Set[str] = set(self.db_paths.values())
        for db in attach:
            if db not in self.db_paths:
                raise ValueError(f"Database '{db}' not configured.")
            attach_dict[db] = self.db_paths[db]

        def authorizer_callback(action: int, arg1: str | None, arg2: str | None, dbname: str | None, source: str | None) -> int:
            if action == sqlite3.SQLITE_ATTACH:
                if arg1 not in allowed_dbs:
                    print(f"ATTACH {arg1} denied")
                    return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        def connector() -> sqlite3.Connection:
            conn = sqlite3.connect(path, isolation_level=None if autocommit else 'DEFERRED')
            conn.set_authorizer(authorizer_callback)
            return conn

        db_connection = aiosqlite.Connection(connector, iter_chunk_size=64)
        return DBWrapperConnection(db_connection, readonly, attach_dict)
