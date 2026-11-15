from abc import ABC, abstractmethod
from typing import List, Tuple, Any

class IQueryExecutor(ABC):
    """صرفا عملیات خواندن داده ها"""
    @abstractmethod
    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[Any]:
        pass

    @abstractmethod
    def validate_integrity_constraint(self, entity_name: str, field_name: str, field_value: int | str) -> bool:
        """کنترل وجود مقدار تکراری قبل از درج رکورد"""
        pass