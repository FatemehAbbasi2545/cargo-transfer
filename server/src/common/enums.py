from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"           
    CARGO_OWNER = "cargo_owner" # صاحب بار
    CARGO_CARRIER = "cargo_carrier" # حمل کننده بار

class TransportType(Enum):
    GROUND = "ground" # حمل زمینی
    AIR = "air" # حمل هوایی
    SEA = "sea" # حمل دریایی

class QueryType(Enum):
    INSERT = 'insert'
    UPDATE = 'update'
    DELETE = 'delete'
    SELECT = "select"
    CREATE_TABLE = 'create_table'