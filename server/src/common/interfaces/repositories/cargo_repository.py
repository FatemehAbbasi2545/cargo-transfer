from abc import ABC, abstractmethod
from typing import List
from src.common.entities.cargo import Cargo

class ICargoRepository(ABC):
    @abstractmethod
    def save(self, cargo: Cargo): ...

    @abstractmethod
    def get_by_owner(self, owner_id: int) -> List[Cargo]: ...

    @abstractmethod
    def get_all(self) -> List[Cargo]: ...

    @abstractmethod
    def get_by_id(self, cargo_id: int) -> Cargo | None: ...
