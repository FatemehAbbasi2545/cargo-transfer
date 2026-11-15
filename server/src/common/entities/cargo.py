from src.common.enums import TransportType

class Cargo:
    def __init__(self, cargo_id: int = None, owner_id: int = None,
                title: str = None, description: str = None, weight: float = None,
                origin: str = None, destination: str = None,
                transport_type: TransportType = None, created_at: str = None):
        self.cargo_id = cargo_id
        self.owner_id = owner_id
        self.title = title
        self.description = description
        self.weight = weight
        self.origin = origin
        self.destination = destination
        self.transport_type = transport_type
        self.created_at = created_at

    def __repr__(self):
        return f'id: {self.cargo_id}, owner: {self.owner_id}, {self.title}, {self.weight}, {self.origin}, {
            self.description}, {self.transport_type}'
