from abc import ABC, abstractmethod

from src.common.interfaces.data_access.query_executor import IQueryExecutor
from src.common.interfaces.data_access.transaction_executor import ITransactionExecutor
from src.common.interfaces.repositories.user_repository import IUserRepository
from src.common.interfaces.repositories.cargo_repository import ICargoRepository
from src.common.interfaces.repositories.cargo_offer_repository import ICargoOfferRepository

class IRepositoryFactory(ABC):
    """Abstract Factory: contract for creating a family of repositories.

    To support a new database (e.g. PostgreSQL), implement this interface
    in a new factory class — no other layer needs to change.
    """

    @abstractmethod
    def create_user_repository(self) -> IUserRepository: ...

    @abstractmethod
    def create_cargo_repository(self) -> ICargoRepository: ...

    @abstractmethod
    def create_cargo_offer_repository(self) -> ICargoOfferRepository: ...
