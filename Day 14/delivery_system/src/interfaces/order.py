from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Order:
    id: int
    restaurant_id: int
    items: List[Dict]
    status: str
    total_price: float
    delivery_lat: float
    delivery_lon: float
