from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.domain.DTO.response import Response
from src.domain.entities.user import User
from src.domain.exceptions import PermissionDeniedError
from src.domain.interfaces.business.cargo_business_management import ICargoBusinessManagement
from src.presentation.api.routes import auth
from src.presentation.api.schemas import (
    CargoResponse, CargoListResponse, CargoOfferResponse, CargoOfferListResponse,
    SubmitCargoRequest, SubmitPriceOfferRequest,
)

router = APIRouter(prefix="/cargos", tags=["cargo"])
cargo_service: ICargoBusinessManagement = None
security = HTTPBasic()

def current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> User:
    response = auth.user_service.login(credentials.username, credentials.password)
    if not response.success:
        raise HTTPException(401, "Invalid username or password.", headers={"WWW-Authenticate": "Basic"})
    return response.data

def business_response(operation: Callable[[], Response]) -> Response:
    """Translate both raised and returned business failures into HTTP errors."""
    try:
        response = operation()
    except PermissionDeniedError as error:
        raise HTTPException(403, error.message) from error
    if not response.success:
        message = response.message or "Operation failed."
        if message == "Cargo not found.":
            raise HTTPException(404, message)
        if message == "Only the cargo owner can view offers for this cargo.":
            raise HTTPException(403, message)
        raise HTTPException(400, message)
    return response


@router.post("", response_model=CargoResponse, status_code=201)
def submit_cargo_request(payload: SubmitCargoRequest, user: Annotated[User, Depends(current_user)]):
    response = business_response(lambda: cargo_service.submit_cargo_request(
        user, payload.title, payload.description, payload.weight,
        payload.origin, payload.destination, payload.transport_type,
    ))
    return CargoResponse(success=True, message=response.message or "", data=response.data)

@router.get("", response_model=CargoListResponse)
def get_all_cargos(user: Annotated[User, Depends(current_user)]):
    response = business_response(lambda: cargo_service.get_all_cargos(user))
    return CargoListResponse(success=True, data=response.data)

@router.get("/mine", response_model=CargoListResponse)
def get_cargos_of_owner(user: Annotated[User, Depends(current_user)]):
    response = business_response(lambda: cargo_service.get_cargos_of_owner(user))
    return CargoListResponse(success=True, data=response.data)

@router.post("/{cargo_id}/offers", response_model=CargoOfferResponse, status_code=201)
def submit_price_offer(
    cargo_id: Annotated[int, Path(gt=0)], 
    payload: SubmitPriceOfferRequest,
    user: Annotated[User, Depends(current_user)],
):
    response = business_response(lambda: cargo_service.submit_price_offer(
        user, cargo_id, payload.price, payload.message,
    ))
    return CargoOfferResponse(success=True, message=response.message or "", data=response.data)

@router.get("/{cargo_id}/offers", response_model=CargoOfferListResponse)
def get_offers_for_cargo(
    cargo_id: Annotated[int, Path(gt=0)], user: Annotated[User, Depends(current_user)],
):
    response = business_response(lambda: cargo_service.get_offers_for_cargo(user, cargo_id))
    return CargoOfferListResponse(success=True, data=response.data)
