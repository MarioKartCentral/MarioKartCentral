"""
DuckDB administrative commands for schema management.
"""

from dataclasses import dataclass
from common.data.commands import Command
from common.data.duckdb.models import ALL_DUCKDB_TABLES


@dataclass
class SetupDuckDBSchemaCommand(Command[None]):
    """Initialize DuckDB schema with all required tables and indexes."""
    
    async def handle(self, db_wrapper, s3_wrapper) -> None:
        async with db_wrapper.duckdb.connection() as conn:
            # Then create/update tables
            for table_cls in ALL_DUCKDB_TABLES:
                # DuckDB can execute multiple statements in a single command
                create_statements = table_cls.get_create_table_command()
                await conn.execute(create_statements)
