"""Client-side data read from JSON responses; independent of server entities."""
from dataclasses import dataclass
from typing import Any

@dataclass
class Response:
    success: bool
    message: str | None = None
    data: Any = None

@dataclass
class User:
    user_id: int
    user_name: str
    role: str

@dataclass
class Cargo:
    cargo_id: int
    owner_id: int
    title: str
    description: str | None
    weight: float
    origin: str
    destination: str
    transport_type: str
    created_at: str | None = None

@dataclass
class CargoOffer:
    offer_id: int
    cargo_id: int
    carrier_id: int
    price: float
    message: str | None = None
    created_at: str | None = None
