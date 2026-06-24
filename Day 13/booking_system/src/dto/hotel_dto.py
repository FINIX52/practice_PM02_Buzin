from pydantic import BaseModel
from typing import Optional


class HotelCreateDTO(BaseModel):
    name: str
    address: str
    phone: str
    rating: Optional[float] = 0.0


class HotelResponseDTO(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    rating: float
