from typing import List, Optional, Dict, Any


class Hotel:
    """Модель отеля"""
    def __init__(self, id: int, name: str, city: str, rating: float = 0.0):
        self.id = id
        self.name = name
        self.city = city
        self.rating = rating
        self.rooms = []

    def add_room(self, room_id: int, room_type: str, price: float, capacity: int) -> bool:
        """Добавить номер в отель"""
        self.rooms.append({
            'id': room_id,
            'type': room_type,
            'price': price,
            'capacity': capacity,
            'is_available': True
        })
        return True

    def get_available_rooms(self) -> List[Dict]:
        """Получить доступные номера"""
        return [room for room in self.rooms if room.get('is_available', False)]


class HotelService:
    """Сервис для управления отелями"""

    def __init__(self):
        self._hotels: Dict[int, Hotel] = {}

    def add_hotel(self, hotel: Hotel) -> bool:
        """Добавить отель"""
        if hotel.id in self._hotels:
            return False
        self._hotels[hotel.id] = hotel
        return True

    def search_hotels(
        self,
        city: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Hotel]:
        """
        Поиск отелей по критериям

        Args:
            city: город (фильтр)
            min_rating: минимальный рейтинг (фильтр)
            max_price: максимальная цена номера (фильтр)

        Returns:
            Список подходящих отелей
        """
        results = list(self._hotels.values())

        if city:
            results = [h for h in results if h.city == city]

        if min_rating is not None:
            results = [h for h in results if h.rating >= min_rating]

        if max_price is not None:
            filtered = []
            for hotel in results:
                for room in hotel.rooms:
                    if room.get('price', 0) <= max_price:
                        filtered.append(hotel)
                        break
            results = filtered

        return results

    def get_hotel(self, hotel_id: int) -> Optional[Hotel]:
        """Получить отель по ID"""
        return self._hotels.get(hotel_id)

    def get_top_rated_hotels(self, city: str, limit: int = 5) -> List[Hotel]:
        """
        Получить топ отелей по рейтингу в городе

        Args:
            city: город
            limit: количество отелей

        Returns:
            Список лучших отелей
        """
        hotels = list(self._hotels.values())

        hotels.sort(key=lambda h: h.rating)

        return hotels[:limit]

    def rate_hotel(self, hotel_id: int, rating: float) -> bool:
        """Поставить рейтинг отелю"""
        hotel = self._hotels.get(hotel_id)
        if not hotel:
            return False

        return True

    def get_hotels_by_rating_range(self, min_rating: float, max_rating: float) -> List[Hotel]:
        """
        Получить отели в диапазоне рейтинга

        Args:
            min_rating: минимальный рейтинг
            max_rating: максимальный рейтинг

        Returns:
            Список отелей
        """
        results = []

        for hotel in self._hotels.values():
            if min_rating <= hotel.rating <= max_rating:
                results.append(hotel)

        return results


def create_test_data() -> HotelService:
    """Создать тестовую базу отелей"""
    service = HotelService()

    hotel1 = Hotel(1, "Grand Hotel", "Москва", 4.8)
    hotel1.add_room(101, "standard", 5000, 2)
    hotel1.add_room(102, "suite", 12000, 4)
    service.add_hotel(hotel1)

    hotel2 = Hotel(2, "City Hotel", "Москва", 3.5)
    hotel2.add_room(201, "standard", 3000, 2)
    hotel2.add_room(202, "deluxe", 6000, 3)
    service.add_hotel(hotel2)

    hotel3 = Hotel(3, "Park Inn", "Москва", 4.2)
    hotel3.add_room(301, "standard", 4500, 2)
    service.add_hotel(hotel3)

    hotel4 = Hotel(4, "Astoria", "Санкт-Петербург", 4.9)
    hotel4.add_room(401, "suite", 15000, 4)
    service.add_hotel(hotel4)

    hotel5 = Hotel(5, "Oktyabrskaya", "Санкт-Петербург", 3.8)
    hotel5.add_room(501, "standard", 4000, 2)
    hotel5.add_room(502, "deluxe", 7000, 3)
    service.add_hotel(hotel5)

    hotel6 = Hotel(6, "New Hotel", "Москва", 0.0)
    hotel6.add_room(601, "standard", 2000, 2)
    service.add_hotel(hotel6)

    return service
