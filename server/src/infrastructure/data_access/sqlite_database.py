import sqlite3
from typing import List, Tuple, Any

from src.common.interfaces.data_access.database_connection import IDatabaseConnection
from src.common.interfaces.data_access.query_executor import IQueryExecutor
from src.common.interfaces.data_access.transaction_executor import ITransactionExecutor
from src.common.exceptions import DatabaseError
from src.common.enums import QueryType

class SQLiteDatabase(IDatabaseConnection, IQueryExecutor, ITransactionExecutor):
    """Singleton: only one instance (and thus one SQLite connection) exists."""

    _instance = None

    def __new__(cls, db_path: str = "app.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup(db_path)
        return cls._instance

    def _setup(self, db_path: str):
        self.__db_path = db_path
        self.__connection = None
        self.connect()

    def connect(self):
        try:
            if self.__connection:
                return self.__connection
            else:
                self.__connection = sqlite3.connect(self.__db_path, check_same_thread=False)
                self.__connection.row_factory = sqlite3.Row
                return self.__connection
        except sqlite3.Error as e:
            raise DatabaseError(f"Unable to connect to SQLite database. {e.args[0]}")

    def is_connected(self) -> bool:
        return self.__connection is not None

    def close(self) -> None:
        if self.__connection:
            self.__connection.close()
            self.__connection = None

    @classmethod
    def reset_instance(cls) -> None:
        """For tests: drop the singleton so a fresh instance can be created."""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        try:
            with self.connect() as connection:
                cursor = connection.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except DatabaseError as error:
            raise error
        except sqlite3.Error as e:
            raise DatabaseError(f"Error executing query: {e.args[0]}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def validate_integrity_constraint(self, entity_name: str, field_name: str, field_value: int | str) -> bool:
        try:
            with self.connect() as connection:
                cursor = connection.cursor()
                query = f"SELECT 1 FROM {entity_name} WHERE {field_name} = ?"
                cursor.execute(query, (field_value,))
                return cursor.fetchone() is None
        except DatabaseError as error:
            raise error
        except sqlite3.Error as e:
            raise DatabaseError(e.args[0])
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def execute_transaction(self, query_type: QueryType, query: str, params: Tuple[Any, ...] = ()) -> int:
        try:
            with self.connect() as connection:
                cursor = connection.cursor()
                cursor.execute(query, params)
                connection.commit()
                return cursor.lastrowid if query_type.value == 'insert' else cursor.rowcount
        except DatabaseError as error:
            raise error
        except sqlite3.IntegrityError:
            raise DatabaseError('Integrity constraint violated.')
        except sqlite3.Error as e:
            raise DatabaseError(f"Error during commit: {e.args[0]}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()