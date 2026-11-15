from typing import List

from src.common.entities.user import User
from src.common.interfaces.repositories.user_repository import IUserRepository
from src.common.interfaces.data_access.query_executor import IQueryExecutor
from src.common.interfaces.data_access.transaction_executor import ITransactionExecutor
from src.common.exceptions import DatabaseError
from src.common.enums import QueryType

class SQLiteUserRepository(IUserRepository):
    _TABLE = "User"
    _COLUMNS = "(name, user_name, password, phone_number, role)"

    def __init__(self, query_executor: IQueryExecutor, transaction_executor: ITransactionExecutor):
        self._query = query_executor
        self._transaction = transaction_executor

        self._ensure_schema()

    def _ensure_schema(self):
        self._transaction.execute_transaction(
            QueryType.CREATE_TABLE,
            """
                CREATE TABLE IF NOT EXISTS User (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    user_name TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    phone_number TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL CHECK(role IN (  
                        'admin', 'cargo_owner', 'cargo_carrier'  
                    )),
                    created_at TEXT DEFAULT (datetime('now', 'localtime')) 
                )
            """
        )

    def save(self, user: User):
        try:
            if not self._query.validate_integrity_constraint('User', 'user_name', user.user_name):
                raise ValueError(f"Username {user.user_name} is already taken.")

            if not self._query.validate_integrity_constraint('User', 'phone_number', user.phone_number):
                raise ValueError("A user with this phone number already exists.")
        except ValueError as error:
            raise DatabaseError(error.args[0])
        except DatabaseError as error:
            raise error
            
        query = (
            f"INSERT INTO {self._TABLE} {self._COLUMNS} "
            "VALUES (?, ?, ?, ?, ?)"
        )
        params = (user.name, user.user_name, user.password, user.phone_number, user.role) 
        uid = self._transaction.execute_transaction(QueryType.INSERT, query, params)
        user.user_id = uid

    def get_by_username(self, user_name: str) -> User | None:
        query = f"SELECT * FROM {self._TABLE} WHERE user_name = ?"
        rows = self._query.execute_query(query, (user_name,))
        return self._row_to_user(rows[0]) if rows else None

    def get_all_users(self) -> List[User]:
        query = f"SELECT * FROM {self._TABLE} ORDER BY user_id"
        rows = self._query.execute_query(query)
        return [self._row_to_user(row) for row in rows if row]

    def update_password(self, user_id: int, new_password: str) -> bool:
        query = f"UPDATE {self._TABLE} SET password = ? WHERE user_id = ?"
        rows_affected = self._transaction.execute_transaction(
            QueryType.UPDATE, query, (new_password, user_id)
        )
        return rows_affected > 0

    def _row_to_user(self, row) -> User:
        return User(
            user_id=row["user_id"],
            name=row["name"],
            user_name=row["user_name"],
            password=row["password"],
            phone_number=row["phone_number"],
            role=row["role"],
        )
    