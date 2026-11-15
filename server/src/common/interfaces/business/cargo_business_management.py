from abc import ABC, abstractmethod

from src.common.entities.user import User
from src.common.DTO.response import Response
from src.common.enums import TransportType

class ICargoBusinessManagement(ABC):
    @abstractmethod
    def submit_cargo_request(self, owner: User, title: str, description: str, weight: float,
        origin: str, destination: str, transport_type: TransportType) -> Response:
        pass

    @abstractmethod
    def get_all_cargos(self, requester: User) -> Response:
        pass

    @abstractmethod
    def get_cargos_of_owner(self, owner: User) -> Response:
        pass

    @abstractmethod
    def submit_price_offer(self, carrier, cargo_id: int, price: float, message: str = None) -> Response:
        pass

    @abstractmethod
    def get_offers_for_cargo(self, requester: User, cargo_id: int) -> Response:
        pass