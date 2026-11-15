from src.domain.entities.cargo import Cargo
from src.domain.interfaces.repositories.cargo_repository import ICargoRepository
from src.domain.interfaces.data_access.query_executor import IQueryExecutor
from src.domain.interfaces.data_access.transaction_executor import ITransactionExecutor
from src.domain.enums import QueryType, TransportType

class SQLiteCargoRepository(ICargoRepository):
    _TABLE = "Cargo"

    def __init__(self, query_executor: IQueryExecutor, transaction_executor: ITransactionExecutor):
        self._query = query_executor
        self._transaction = transaction_executor
        self._ensure_schema()

    def _ensure_schema(self):
        self._transaction.execute_transaction(
            QueryType.CREATE_TABLE,
            """
                CREATE TABLE IF NOT EXISTS Cargo (
                    cargo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    weight REAL NOT NULL,
                    origin TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    transport_type TEXT NOT NULL CHECK(transport_type IN (
                        'ground', 'air', 'sea'
                    )),
                    created_at TEXT DEFAULT (datetime('now', 'localtime')),
                    FOREIGN KEY (owner_id) REFERENCES User(user_id)
                )
            """
        )

    def save(self, cargo: Cargo):
        query = (
            f"INSERT INTO {self._TABLE} (owner_id, title, description, weight, origin, destination, transport_type) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        params = (cargo.owner_id, cargo.title, cargo.description, cargo.weight,
                  cargo.origin, cargo.destination,
                  cargo.transport_type.value if isinstance(cargo.transport_type, TransportType) else cargo.transport_type)
        uid = self._transaction.execute_transaction(QueryType.INSERT, query, params)
        cargo.cargo_id = uid

    def get_by_owner(self, owner_id: int) -> list[Cargo]:
        query = f"SELECT * FROM {self._TABLE} WHERE owner_id = ? ORDER BY cargo_id DESC"
        rows = self._query.execute_query(query, (owner_id,))
        return [self._row_to_cargo(row) for row in rows if row]

    def get_all(self) -> list[Cargo]:
        query = f"SELECT * FROM {self._TABLE} ORDER BY cargo_id DESC"
        rows = self._query.execute_query(query)
        return [self._row_to_cargo(row) for row in rows if row]

    def get_by_id(self, cargo_id: int) -> Cargo | None:
        query = f"SELECT * FROM {self._TABLE} WHERE cargo_id = ?"
        rows = self._query.execute_query(query, (cargo_id,))
        return self._row_to_cargo(rows[0]) if rows else None

    def _row_to_cargo(self, row) -> Cargo:
        return Cargo(
            cargo_id=row["cargo_id"],
            owner_id=row["owner_id"],
            title=row["title"],
            description=row["description"],
            weight=row["weight"],
            origin=row["origin"],
            destination=row["destination"],
            transport_type=row["transport_type"],
            created_at=row["created_at"],
        )
