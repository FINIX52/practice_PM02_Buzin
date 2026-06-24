from dataclasses import dataclass

@dataclass
class MenuItem:
    id: int
    restaurant_id: int
    name: str
    price: float
    is_available: bool
