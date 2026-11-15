from abc import ABC, abstractmethod
from typing import Tuple, Any

from src.domain.enums import QueryType

class ITransactionExecutor(ABC):
    @abstractmethod
    def execute_transaction(self, query_type: QueryType, query: str, params: Tuple[Any, ...] = ()) -> int:
        """(INSERT/UPDATE/DELETE) and Commit"""
        pass