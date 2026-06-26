from typing import List, Dict, Any
from src.core.domain import Hotel, Room


class HotelFactory:
    @staticmethod
    def create_hotel(
        hotel_id: int = 1,
        name: str = "Test Hotel",
        city: str = "Москва",
        rating: float = 4.0,
        rooms_count: int = 1
    ) -> Hotel:
        hotel = Hotel(hotel_id, name, city, rating)
        for i in range(rooms_count):
            room = Room(
                room_id=100 + i,
                room_type="standard",
                price=5000 + (i * 1000),
                capacity=2
            )
            hotel.add_room(room)
        return hotel

    @staticmethod
    def create_test_hotels() -> List[Hotel]:
        hotels = []
        for i in range(1, 6):
            hotel = Hotel(
                i,
                f"Hotel {i}",
                ["Москва", "Санкт-Петербург", "Казань"][i % 3],
                float(i * 0.8 + 0.5)
            )
            hotel.add_room(Room(100 + i, "standard", 3000 + (i * 500), 2))
            hotels.append(hotel)
        return hotels
