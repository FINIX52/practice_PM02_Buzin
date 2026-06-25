import pytest
from src.hotel import Hotel, HotelService, create_test_data


class TestHotel:
    """Тесты для класса Hotel"""

    def test_hotel_creation(self):
        """Создание отеля"""
        hotel = Hotel(1, "Test Hotel", "Москва", 4.5)
        assert hotel.id == 1
        assert hotel.name == "Test Hotel"
        assert hotel.city == "Москва"
        assert hotel.rating == 4.5

    def test_add_room_success(self):
        """Добавление номера в отель"""
        hotel = Hotel(1, "Test Hotel", "Москва", 4.5)
        result = hotel.add_room(101, "standard", 5000, 2)
        assert result is True
        assert len(hotel.rooms) == 1
        assert hotel.rooms[0]['type'] == "standard"

    def test_get_available_rooms(self):
        """Получение доступных номеров"""
        hotel = Hotel(1, "Test Hotel", "Москва", 4.5)
        hotel.add_room(101, "standard", 5000, 2)
        rooms = hotel.get_available_rooms()
        assert len(rooms) == 1


class TestHotelService:
    """Тесты для HotelService"""

    @pytest.fixture
    def service(self):
        """Фикстура с тестовыми данными"""
        return create_test_data()

    def test_add_hotel_success(self):
        """Добавление нового отеля"""
        service = HotelService()
        hotel = Hotel(10, "New Hotel", "Казань", 4.0)
        result = service.add_hotel(hotel)
        assert result is True
        assert service.get_hotel(10) is not None

    def test_add_hotel_duplicate(self):
        """Добавление отеля с существующим ID"""
        service = HotelService()
        hotel1 = Hotel(1, "Hotel 1", "Москва", 4.0)
        hotel2 = Hotel(1, "Hotel 2", "Москва", 4.0)
        service.add_hotel(hotel1)
        result = service.add_hotel(hotel2)
        assert result is False

    def test_search_hotels_by_city(self, service):
        """Поиск отелей по городу"""
        results = service.search_hotels(city="Москва")
        assert len(results) == 4

    def test_search_hotels_by_city_case(self, service):
        """Поиск отелей по городу (регистронезависимый)"""
        results = service.search_hotels(city="москва")
        assert len(results) == 0

    def test_search_hotels_by_min_rating(self, service):
        """Поиск отелей по минимальному рейтингу"""
        results = service.search_hotels(min_rating=4.0)
        assert len(results) == 3

    def test_search_hotels_by_city_and_rating(self, service):
        """Поиск отелей по городу и рейтингу"""
        results = service.search_hotels(city="Москва", min_rating=4.0)
        assert len(results) == 2

    def test_search_hotels_by_max_price(self, service):
        """Поиск отелей по максимальной цене"""
        results = service.search_hotels(max_price=4000)
        assert len(results) == 3

    def test_get_top_rated_hotels_default_limit(self, service):
        """Получение топ отелей (лимит по умолчанию 5)"""
        results = service.get_top_rated_hotels("Москва")
        assert len(results) == 5

    def test_get_top_rated_hotels_with_limit(self, service):
        """Получение топ отелей с указанным лимитом"""
        results = service.get_top_rated_hotels("Москва", limit=2)
        assert len(results) == 2

    def test_rate_hotel_success(self, service):
        """Успешное изменение рейтинга отеля"""
        result = service.rate_hotel(1, 5.0)
        assert result is True
        hotel = service.get_hotel(1)
        assert hotel.rating == 4.8

    def test_rate_hotel_not_found(self, service):
        """Изменение рейтинга несуществующего отеля"""
        result = service.rate_hotel(999, 5.0)
        assert result is False

    def test_get_hotels_by_rating_range(self, service):
        """Получение отелей в диапазоне рейтинга"""
        results = service.get_hotels_by_rating_range(3.5, 4.5)
        assert len(results) == 3

    def test_get_hotels_by_rating_range_zero_rating(self, service):
        """Получение отелей с нулевым рейтингом"""
        results = service.get_hotels_by_rating_range(0.0, 0.0)
        assert len(results) == 1

    def test_search_hotels_empty(self, service):
        """Поиск отелей без результатов"""
        results = service.search_hotels(city="Казань")
        assert len(results) == 0
