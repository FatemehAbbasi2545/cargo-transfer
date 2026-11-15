from src.common.entities.cargo_offer import CargoOffer
from src.common.enums import QueryType
from src.common.interfaces.repositories.cargo_offer_repository import ICargoOfferRepository
from src.common.interfaces.data_access.query_executor import IQueryExecutor
from src.common.interfaces.data_access.transaction_executor import ITransactionExecutor

class SQLiteCargoOfferRepository(ICargoOfferRepository):
    _TABLE = "CargoOffer"

    def __init__(self, query_executor: IQueryExecutor, transaction_executor: ITransactionExecutor):
        self._query = query_executor
        self._transaction = transaction_executor
        self._ensure_schema()

    def _ensure_schema(self):
        self._transaction.execute_transaction(
            QueryType.CREATE_TABLE,
            """
                CREATE TABLE IF NOT EXISTS CargoOffer (
                    offer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cargo_id INTEGER NOT NULL,
                    carrier_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    message TEXT,
                    created_at TEXT DEFAULT (datetime('now', 'localtime')),
                    FOREIGN KEY (cargo_id) REFERENCES Cargo(cargo_id),
                    FOREIGN KEY (carrier_id) REFERENCES User(user_id)
                )
            """
        )

    def save(self, offer: CargoOffer):
        query = (
            f"INSERT INTO {self._TABLE} (cargo_id, carrier_id, price, message) "
            "VALUES (?, ?, ?, ?)"
        )
        params = (offer.cargo_id, offer.carrier_id, offer.price, offer.message)
        uid = self._transaction.execute_transaction(QueryType.INSERT, query, params)
        offer.offer_id = uid

    def get_by_cargo(self, cargo_id: int) -> list[CargoOffer]:
        query = f"SELECT * FROM {self._TABLE} WHERE cargo_id = ? ORDER BY offer_id DESC"
        rows = self._query.execute_query(query, (cargo_id,))
        return [self._row_to_offer(row) for row in rows if row]

    def get_by_carrier(self, carrier_id: int) -> list[CargoOffer]:
        query = f"SELECT * FROM {self._TABLE} WHERE carrier_id = ? ORDER BY offer_id DESC"
        rows = self._query.execute_query(query, (carrier_id,))
        return [self._row_to_offer(row) for row in rows if row]

    def _row_to_offer(self, row) -> CargoOffer:
        return CargoOffer(
            offer_id=row["offer_id"],
            cargo_id=row["cargo_id"],
            carrier_id=row["carrier_id"],
            price=row["price"],
            message=row["message"],
            created_at=row["created_at"],
        )
