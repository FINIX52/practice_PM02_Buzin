from dataclasses import dataclass
from typing import Optional, List


@dataclass
class HotelCreateDTO:
    name: str
    city: str
    rating: float = 0.0


@dataclass
class HotelResponseDTO:
    id: int
    name: str
    city: str
    rating: float


@dataclass
class RoomCreateDTO:
    room_type: str
    price: float
    capacity: int


@dataclass
class RoomResponseDTO:
    id: int
    room_type: str
    price: float
    capacity: int
    is_available: bool


@dataclass
class SearchHotelsDTO:
    city: Optional[str] = None
    min_rating: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = 10
