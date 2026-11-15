from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.cargo_offer import CargoOffer

class ICargoOfferRepository(ABC):
    @abstractmethod
    def save(self, offer: CargoOffer): ...

    @abstractmethod
    def get_by_cargo(self, cargo_id: int) -> List[CargoOffer]: ...

    @abstractmethod
    def get_by_carrier(self, carrier_id: int) -> List[CargoOffer]: ...
