from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.core.domain import Hotel, Room
from src.application.dto import SearchHotelsDTO, HotelResponseDTO, RoomResponseDTO


class IHotelRepository(ABC):
    @abstractmethod
    def get_by_id(self, hotel_id: int) -> Optional[Hotel]:
        pass

    @abstractmethod
    def get_all(self) -> List[Hotel]:
        pass

    @abstractmethod
    def add(self, hotel: Hotel) -> Hotel:
        pass

    @abstractmethod
    def update(self, hotel: Hotel) -> Hotel:
        pass

    @abstractmethod
    def delete(self, hotel_id: int) -> bool:
        pass


class IHotelService(ABC):
    @abstractmethod
    def add_hotel(self, hotel: Hotel) -> bool:
        pass

    @abstractmethod
    def search_hotels(self, filters: SearchHotelsDTO) -> List[Hotel]:
        pass

    @abstractmethod
    def get_hotel(self, hotel_id: int) -> Optional[HotelResponseDTO]:
        pass

    @abstractmethod
    def get_top_rated_hotels(self, city: str, limit: int) -> List[HotelResponseDTO]:
        pass

    @abstractmethod
    def rate_hotel(self, hotel_id: int, rating: float) -> bool:
        pass

    @abstractmethod
    def get_hotels_by_rating_range(self, min_rating: float, max_rating: float) -> List[HotelResponseDTO]:
        pass
