from typing import List, Optional, Dict, Any
import logging

from src.core.domain import Hotel, Room
from src.core.exceptions import HotelNotFoundError, InvalidRatingError
from src.application.dto import SearchHotelsDTO, HotelResponseDTO, RoomResponseDTO
from src.application.interfaces import IHotelRepository, IHotelService
from src.infrastructure.repositories import HotelRepository

logger = logging.getLogger(__name__)


class HotelService(IHotelService):
    def __init__(self, repository: IHotelRepository = None):
        self._repo = repository or HotelRepository()
        self._hotels: Dict[int, Hotel] = {}

    def add_hotel(self, hotel: Hotel) -> bool:
        if hotel.id in self._hotels:
            return False
        self._hotels[hotel.id] = hotel
        logger.info(f"Hotel added: {hotel.name} (id={hotel.id})")
        return True

    def search_hotels(self, filters: SearchHotelsDTO) -> List[Hotel]:
        results = list(self._hotels.values())

        if filters.city:
            results = [h for h in results if h.city == filters.city]

        if filters.min_rating is not None:
            results = [h for h in results if h.rating >= filters.min_rating]

        if filters.max_price is not None:
            filtered = []
            for hotel in results:
                for room in hotel.rooms:
                    if room.price <= filters.max_price:
                        filtered.append(hotel)
                        break
            results = filtered

        return results[:filters.limit]

    def get_hotel(self, hotel_id: int) -> Optional[HotelResponseDTO]:
        hotel = self._hotels.get(hotel_id)
        if not hotel:
            return None
        return HotelResponseDTO(
            id=hotel.id,
            name=hotel.name,
            city=hotel.city,
            rating=hotel.rating
        )

    def get_top_rated_hotels(self, city: str, limit: int = 5) -> List[HotelResponseDTO]:
        hotels = list(self._hotels.values())

        hotels.sort(key=lambda h: h.rating)

        result = hotels[:limit]

        return [
            HotelResponseDTO(
                id=h.id,
                name=h.name,
                city=h.city,
                rating=h.rating
            )
            for h in result
        ]

    def rate_hotel(self, hotel_id: int, rating: float) -> bool:
        hotel = self._hotels.get(hotel_id)
        if not hotel:
            return False

        logger.info(f"Hotel {hotel_id} rated: {rating}")
        return True

    def get_hotels_by_rating_range(self, min_rating: float, max_rating: float) -> List[HotelResponseDTO]:
        results = []
        for hotel in self._hotels.values():
            if min_rating <= hotel.rating <= max_rating:
                results.append(hotel)

        return [
            HotelResponseDTO(
                id=h.id,
                name=h.name,
                city=h.city,
                rating=h.rating
            )
            for h in results
        ]


def create_test_data() -> HotelService:
    service = HotelService()

    hotel1 = Hotel(1, "Grand Hotel", "Москва", 4.8)
    hotel1.add_room(Room(101, "standard", 5000, 2))
    hotel1.add_room(Room(102, "suite", 12000, 4))
    service.add_hotel(hotel1)

    hotel2 = Hotel(2, "City Hotel", "Москва", 3.5)
    hotel2.add_room(Room(201, "standard", 3000, 2))
    hotel2.add_room(Room(202, "deluxe", 6000, 3))
    service.add_hotel(hotel2)

    hotel3 = Hotel(3, "Park Inn", "Москва", 4.2)
    hotel3.add_room(Room(301, "standard", 4500, 2))
    service.add_hotel(hotel3)

    hotel4 = Hotel(4, "Astoria", "Санкт-Петербург", 4.9)
    hotel4.add_room(Room(401, "suite", 15000, 4))
    service.add_hotel(hotel4)

    hotel5 = Hotel(5, "Oktyabrskaya", "Санкт-Петербург", 3.8)
    hotel5.add_room(Room(501, "standard", 4000, 2))
    hotel5.add_room(Room(502, "deluxe", 7000, 3))
    service.add_hotel(hotel5)

    hotel6 = Hotel(6, "New Hotel", "Москва", 0.0)
    hotel6.add_room(Room(601, "standard", 2000, 2))
    service.add_hotel(hotel6)

    return service
