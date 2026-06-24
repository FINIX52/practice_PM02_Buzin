from pydantic import BaseModel
from typing import Optional


class RoomCreateDTO(BaseModel):
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    room_type: Optional[str] = "standard"


class RoomResponseDTO(BaseModel):
    id: int
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    is_active: bool
    room_type: str
