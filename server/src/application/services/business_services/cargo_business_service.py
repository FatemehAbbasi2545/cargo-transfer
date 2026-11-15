from src.common.interfaces.repositories.cargo_repository import ICargoRepository
from src.common.interfaces.repositories.cargo_offer_repository import ICargoOfferRepository
from src.common.interfaces.business.cargo_business_management import ICargoBusinessManagement
from src.common.exceptions import DatabaseError, PermissionDeniedError
from src.common.enums import UserRole, TransportType
from src.common.entities.user import User
from src.common.entities.cargo import Cargo
from src.common.entities.cargo_offer import CargoOffer
from src.common.DTO.response import Response

class CargoBusinessService(ICargoBusinessManagement):
    def __init__(self, cargo_repository: ICargoRepository, cargo_offer_repository: ICargoOfferRepository):
        self.cargo_repository = cargo_repository
        self.cargo_offer_repository = cargo_offer_repository

    def submit_cargo_request(self, owner: User, title: str, description: str, weight: float,
                            origin: str, destination: str, transport_type: TransportType) -> Response:
        if owner is None or owner.role != UserRole.CARGO_OWNER.value:
            raise PermissionDeniedError("Only cargo owners can submit cargo requests.")
        cargo = Cargo(owner_id=owner.user_id, title=title, description=description,
                      weight=weight, origin=origin, destination=destination,
                      transport_type=transport_type)
        
        try:
            self.cargo_repository.save(cargo) 
            return Response(True, message=f"Cargo {cargo.title} submitted successfully", data=cargo)
        except (DatabaseError, PermissionDeniedError) as error:
            return Response(False, message=error.message) 

    def get_all_cargos(self, requester: User) -> Response:
        if requester is None:
            raise PermissionDeniedError("You must be logged in.")
        if requester.role == UserRole.CARGO_OWNER.value:
            raise PermissionDeniedError("The requester must be an admin or a cargo carrier.")

        try:
            result: list[Cargo] = self.cargo_repository.get_all()
            return Response(True, data=result)
        except (DatabaseError, PermissionDeniedError) as error:
            return Response(False, message=error.message)

    def get_cargos_of_owner(self, owner: User) -> Response:
        if owner is None or owner.role != UserRole.CARGO_OWNER.value:
            raise PermissionDeniedError("Only cargo owners can request.")
        
        try:
            result : list[Cargo] = self.cargo_repository.get_by_owner(owner.user_id)
            return Response(True, data=result)
        except (DatabaseError, PermissionDeniedError) as error:
            return Response(False, message=error.message)

    def submit_price_offer(self, carrier, cargo_id: int, price: float, message: str = None) -> Response:
        if carrier is None or carrier.role != UserRole.CARGO_CARRIER.value:
            raise PermissionDeniedError("Only cargo carriers can submit price offers.")

        try:
            cargo: Cargo | None = self.cargo_repository.get_by_id(cargo_id)
            if cargo is None:
                raise ValueError("Cargo not found.")
            offer = CargoOffer(cargo_id=cargo_id, carrier_id=carrier.user_id,
                            price=price, message=message)
            self.cargo_offer_repository.save(offer)
            return Response(True, message="Cargo offer submitted successfully", data=offer)
        except (DatabaseError, PermissionDeniedError) as error:
            return Response(False, message=error.message)
        except ValueError as error:
            return Response(False, message=error.args[0])

    def get_offers_for_cargo(self, requester: User, cargo_id: int) -> Response:
        if requester is None:
            raise PermissionDeniedError("You must be logged in.")

        try:
            cargo: Cargo | None = self.cargo_repository.get_by_id(cargo_id)
            if cargo is None:
                return Response(False, message="Cargo not found.")

            # فقط صاحب بار (یا ادمین) می‌تواند پیشنهادات آن بار را ببیند
            is_owner = requester.role == UserRole.CARGO_OWNER.value and cargo.owner_id == requester.user_id
            is_admin = requester.role == UserRole.ADMIN.value
            if not (is_owner or is_admin):
                raise PermissionDeniedError("Only the cargo owner can view offers for this cargo.")

            offers: list[CargoOffer] = self.cargo_offer_repository.get_by_cargo(cargo_id)
            return Response(True, data=offers)
        except (DatabaseError, PermissionDeniedError) as error:
            return Response(False, message=error.message)
