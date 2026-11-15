"""Values in the public API contract used by the desktop UI."""
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    CARGO_OWNER = "cargo_owner"
    CARGO_CARRIER = "cargo_carrier"

class TransportType(Enum):
    GROUND = "ground"
    AIR = "air"
    SEA = "sea"
