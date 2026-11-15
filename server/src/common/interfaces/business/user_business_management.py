from abc import ABC, abstractmethod

from src.common.entities.user import User
from src.common.DTO.response import Response

class IUserBusinessManagement(ABC):
    @abstractmethod
    def register(self, user: User) -> Response:
        pass

    @abstractmethod
    def login(self, user_name: str, password: str) -> Response:
        pass

    @abstractmethod
    def Update_password(self, user_id: int, new_password: str) -> Response:
        pass