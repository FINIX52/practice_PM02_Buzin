from typing import List, Optional
from src.domain.models import Hotel
from src.domain.exceptions import HotelNotFoundError
from src.dto.hotel_dto import HotelCreateDTO, HotelResponseDTO
from src.repositories.hotel_repo import HotelRepository


class HotelService:
    def __init__(self, hotel_repo: HotelRepository):
        self.hotel_repo = hotel_repo

    def create(self, dto: HotelCreateDTO) -> HotelResponseDTO:
        hotel = Hotel(
            id=None,
            name=dto.name,
            address=dto.address,
            phone=dto.phone,
            rating=dto.rating or 0.0
        )
        saved = self.hotel_repo.add(hotel)
        return HotelResponseDTO(
            id=saved.id,
            name=saved.name,
            address=saved.address,
            phone=saved.phone,
            rating=saved.rating
        )

    def get_by_id(self, hotel_id: int) -> Optional[HotelResponseDTO]:
        hotel = self.hotel_repo.get_by_id(hotel_id)
        if not hotel:
            return None
        return HotelResponseDTO(
            id=hotel.id,
            name=hotel.name,
            address=hotel.address,
            phone=hotel.phone,
            rating=hotel.rating
        )

    def get_all(self) -> List[HotelResponseDTO]:
        hotels = self.hotel_repo.get_all()
        return [
            HotelResponseDTO(
                id=h.id,
                name=h.name,
                address=h.address,
                phone=h.phone,
                rating=h.rating
            )
            for h in hotels
        ]
