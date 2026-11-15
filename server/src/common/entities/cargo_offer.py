class CargoOffer:
    def __init__(self, offer_id: int = None, cargo_id: int = None, carrier_id: int = None,
                 price: float = None, message: str = None, created_at: str = None):
        self.offer_id = offer_id
        self.cargo_id = cargo_id
        self.carrier_id = carrier_id
        self.price = price
        self.message = message
        self.created_at = created_at

    def __repr__(self):
            return f'offer_id: {self.offer_id}, cargo_id: {self.cargo_id}, carrier_id: {self.carrier_id}, {
                self.price}, {self.message}'
