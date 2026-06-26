from typing import List, Optional, Dict, Any

from src.core.domain import Hotel, Room
from src.core.exceptions import HotelNotFoundError
from src.application.interfaces import IHotelRepository


class HotelRepository(IHotelRepository):
    def __init__(self):
        self._storage: Dict[int, Hotel] = {}
        self._next_id: int = 1

    def get_by_id(self, hotel_id: int) -> Optional[Hotel]:
        return self._storage.get(hotel_id)

    def get_all(self) -> List[Hotel]:
        return list(self._storage.values())

    def add(self, hotel: Hotel) -> Hotel:
        hotel.id = self._next_id
        self._storage[hotel.id] = hotel
        self._next_id += 1
        return hotel

    def update(self, hotel: Hotel) -> Hotel:
        if hotel.id not in self._storage:
            raise HotelNotFoundError(f"Hotel with id {hotel.id} not found")
        self._storage[hotel.id] = hotel
        return hotel

    def delete(self, hotel_id: int) -> bool:
        if hotel_id in self._storage:
            del self._storage[hotel_id]
            return True
        return False
