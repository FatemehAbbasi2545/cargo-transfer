from abc import ABC, abstractmethod
from typing import List

from src.common.entities.user import User

class IUserRepository(ABC):
    @abstractmethod
    def _ensure_schema(self): ...
    
    @abstractmethod
    def save(self, user: User): ...

    @abstractmethod
    def get_by_username(self, user_name: str) -> User | None: ...

    @abstractmethod
    def get_all_users(self) -> List[User]: ...

    @abstractmethod
    def update_password(self, user_id: int, new_password: str) -> bool: ...

    @abstractmethod
    def _row_to_user(self, row) -> User: ...

    