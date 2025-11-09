from abc import ABC, abstractmethod
from dataclasses import dataclass

class TableModel(ABC):
    @staticmethod
    @abstractmethod
    def get_create_table_command() -> str:
        pass

class IndexModel(ABC):
    @staticmethod
    @abstractmethod
    def get_create_index_command() -> str:
        pass

@dataclass
class DatabaseSchema:
    db_name: str
    tables: list[type[TableModel]]
    indices: list[type[IndexModel]]