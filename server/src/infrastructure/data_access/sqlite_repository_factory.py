from src.common.interfaces.repositories.repository_factory import IRepositoryFactory
from src.infrastructure.data_access.sqlite_user_repository import SQLiteUserRepository
from src.infrastructure.data_access.sqlite_cargo_repository import SQLiteCargoRepository
from src.infrastructure.data_access.sqlite_cargo_offer_repository import SQLiteCargoOfferRepository

class SQLiteRepositoryFactory(IRepositoryFactory):
    """Concrete factory: creates the SQLite-backed repository family.

    Singleton SQLiteDatabase ensures the same connection is shared.
    """

    def __init__(self, db):
        self._db = db

    def create_user_repository(self):
        return SQLiteUserRepository(self._db, self._db)

    def create_cargo_repository(self):
        return SQLiteCargoRepository(self._db, self._db)

    def create_cargo_offer_repository(self):
        return SQLiteCargoOfferRepository(self._db, self._db)
