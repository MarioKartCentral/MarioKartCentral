"""DuckDB wrapper providing async connection management."""

import aioduckdb
from types import TracebackType
import logging
import os

logger = logging.getLogger(__name__)


class DuckDBWrapperConnection:
    """Async context manager for DuckDB connections."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: aioduckdb.Connection | None = None

    async def __aenter__(self) -> aioduckdb.Connection:
        try:
            self.conn = await aioduckdb.connect(database=self.db_path, read_only=False)
            logger.debug(f"Connected to DuckDB at {self.db_path}")
            return self.conn
        except Exception as e:
            logger.error(f"Failed to connect to DuckDB at {self.db_path}: {e}")
            raise

    async def __aexit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        if self.conn:
            try:
                await self.conn.close()
                logger.debug(f"Closed DuckDB connection to {self.db_path}")
            except Exception as e:
                logger.error(f"Error closing DuckDB connection: {e}")
            finally:
                self.conn = None


class DuckDBWrapper:
    """DuckDB wrapper providing connection management."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        logger.info(f"Initialized DuckDB wrapper for {db_path}")

    def connection(self) -> DuckDBWrapperConnection:
        """Create a new connection context manager."""
        return DuckDBWrapperConnection(self.db_path)
    
    def reset_db(self):
        logging.info(f"Resetting DuckDB file: {self.db_path}")
        try:
            os.remove(self.db_path)
        except FileNotFoundError:
            logging.info(f"DuckDB file {self.db_path} not found.")