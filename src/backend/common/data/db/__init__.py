from dataclasses import dataclass
import aiosqlite

# Wrapper over the aiosqlite connection which enables foreign keys
@dataclass
class DBWrapperConnection():
    connection: aiosqlite.Connection
    readonly: bool = False

    async def __aenter__(self) -> aiosqlite.Connection:
        db = await self.connection
        if not self.readonly:
            await db.execute("pragma foreign_keys = ON;")
        return db

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.connection.close()

@dataclass
class DBWrapper():
    db_path: str

    def reset_db(self):
        open(self.db_path, 'w').close()

    def connect(self, readonly=False):
        return DBWrapperConnection(aiosqlite.connect(self.db_path), readonly)