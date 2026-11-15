from fastapi import APIRouter, HTTPException, status

from src.common.DTO.response import Response
from src.common.interfaces.business.user_business_management import IUserBusinessManagement
from src.presentation.api.schemas import (
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    UpdatePasswordRequest, UpdatePasswordResponse,
)

router = APIRouter(tags=["auth"])

# Injection point, set at app startup (see app.py)
user_service: IUserBusinessManagement = None

@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    """Login endpoint — delegates to the existing UserBusinessService."""
    response: Response = user_service.login(payload.user_name, payload.password)

    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response.message or "Invalid username or password.",
        )

    user = response.data
    return LoginResponse(
        success=True,
        message="Login successful",
        user_id=user.user_id,
        user_name=user.user_name,
        role=user.role,
    )

@router.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> RegisterResponse:
    """Register endpoint — delegates to the existing UserBusinessService."""
    from src.common.entities.user import User

    user = User(
        name=payload.name,
        user_name=payload.user_name,
        password=payload.password,
        phone_number=payload.phone_number,
        role=payload.role,
    )

    response: Response = user_service.register(user)

    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=response.message or "Registration failed.",
        )

    return RegisterResponse(
        success=True,
        message=response.message or "User registered successfully",
        user_id=user.user_id,
    )

@router.patch("/auth/update-password", response_model=UpdatePasswordResponse)
def update_password(payload: UpdatePasswordRequest) -> UpdatePasswordResponse:
    """Update a user's password through the existing business service."""
    response: Response = user_service.Update_password(payload.user_id, payload.new_password)

    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.message or "Password update failed.",
        )

    return UpdatePasswordResponse(
        success=True,
        message=response.message or "Password updated successfully",
    )