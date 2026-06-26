from typing import List, Optional

from src.application.services import HotelService
from src.application.dto import SearchHotelsDTO, HotelResponseDTO
from src.core.domain import Hotel


class HotelAPI:
    def __init__(self, service: HotelService):
        self.service = service

    def add_hotel(self, name: str, city: str, rating: float = 0.0) -> bool:
        hotel = Hotel(None, name, city, rating)
        return self.service.add_hotel(hotel)

    def search(self, city: Optional[str] = None, min_rating: Optional[float] = None) -> List[HotelResponseDTO]:
        filters = SearchHotelsDTO(city=city, min_rating=min_rating)
        hotels = self.service.search_hotels(filters)
        return [
            HotelResponseDTO(
                id=h.id,
                name=h.name,
                city=h.city,
                rating=h.rating
            )
            for h in hotels
        ]
