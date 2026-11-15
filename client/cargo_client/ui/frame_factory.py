from cargo_client.ui.api_client import APIClient
from tkinter import Frame
from typing import Callable

from cargo_client.enums import UserRole
from cargo_client.models import User
from cargo_client.ui.frames.cargo_request_frame import CargoRequestFrame
from cargo_client.ui.frames.cargo_offers_frame import CargoOffersFrame

class FrameFactory:
    """Factory Pattern: creates the appropriate post-login frame based on user role."""

    _REGISTRY = {
        UserRole.CARGO_OWNER: CargoRequestFrame,
        UserRole.CARGO_CARRIER: CargoOffersFrame,
    }

    @classmethod
    def create_role_frame(
        cls,
        role: UserRole,
        container: Frame,
        api_client: APIClient,
        current_user: User,
    ) -> Frame:
        frame_cls = cls._REGISTRY.get(role)
        if frame_cls is None:
            raise ValueError(f"No frame registered for role: {role}")
        return frame_cls(container, api_client, current_user)

    @classmethod
    def register(cls, role: UserRole, frame_cls) -> None:
        """Allow new roles/frames to be added without modifying this class (Open/Closed)."""
        cls._REGISTRY[role] = frame_cls
