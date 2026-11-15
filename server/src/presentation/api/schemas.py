from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.common.enums import TransportType, UserRole

class LoginRequest(BaseModel):
    user_name: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")

class UpdatePasswordRequest(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID")
    new_password: str = Field(..., min_length=8, description="New password (min 8 chars)")

class UpdatePasswordResponse(BaseModel):
    success: bool
    message: str

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Full name")
    user_name: str = Field(..., min_length=3, description="Username (min 3 chars)")
    phone_number: str = Field(..., min_length=10, max_length=15, description="Mobile phone")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    confirm_password: str = Field(..., min_length=8, description="Password confirmation")
    role: str = Field("cargo_owner", description="cargo_owner | cargo_carrier")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = {UserRole.CARGO_OWNER.value, UserRole.CARGO_CARRIER.value}
        if v not in allowed:
            raise ValueError(f"role must be one of: {', '.join(allowed)}")
        return v

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("The password and password confirmation values must be the same.")
        return self

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: int | None = None

class LoginResponse(BaseModel):
    success: bool
    message: str = ""
    user_id: int | None = None
    user_name: str | None = None
    role: str | None = None

class ErrorResponse(BaseModel):
    detail: str

class SubmitCargoRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = ""
    weight: float = Field(..., gt=0, allow_inf_nan=False)
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    transport_type: TransportType

class CargoData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cargo_id: int
    owner_id: int
    title: str
    description: str | None = None
    weight: float
    origin: str
    destination: str
    transport_type: TransportType
    created_at: str | None = None

class CargoResponse(BaseModel):
    success: bool
    message: str = ""
    data: CargoData

class CargoListResponse(BaseModel):
    success: bool
    message: str = ""
    data: list[CargoData]

class SubmitPriceOfferRequest(BaseModel):
    price: float = Field(..., gt=0, allow_inf_nan=False)
    message: str | None = None

class CargoOfferData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    offer_id: int
    cargo_id: int
    carrier_id: int
    price: float
    message: str | None = None
    created_at: str | None = None

class CargoOfferResponse(BaseModel):
    success: bool
    message: str = ""
    data: CargoOfferData

class CargoOfferListResponse(BaseModel):
    success: bool
    message: str = ""
    data: list[CargoOfferData]
