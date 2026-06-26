import pytest
from src.application.services import HotelService, create_test_data
from src.application.dto import SearchHotelsDTO
from src.core.domain import Hotel, Room


@pytest.fixture
def service():
    return create_test_data()


class TestHotelService:
    def test_add_hotel_success(self):
        service = HotelService()
        hotel = Hotel(10, "New Hotel", "Казань", 4.0)
        result = service.add_hotel(hotel)
        assert result is True

    def test_add_hotel_duplicate(self):
        service = HotelService()
        hotel1 = Hotel(1, "Hotel 1", "Москва", 4.0)
        hotel2 = Hotel(1, "Hotel 2", "Москва", 4.0)
        service.add_hotel(hotel1)
        result = service.add_hotel(hotel2)
        assert result is False

    def test_search_by_city(self, service):
        filters = SearchHotelsDTO(city="Москва")
        results = service.search_hotels(filters)
        assert len(results) == 4

    def test_search_by_city_case_sensitive(self, service):
        """Тест: регистрозависимость — ошибка, должно вернуть 0"""
        filters = SearchHotelsDTO(city="москва")
        results = service.search_hotels(filters)
        assert len(results) == 0

    def test_search_by_min_rating(self, service):
        filters = SearchHotelsDTO(min_rating=4.0)
        results = service.search_hotels(filters)
        assert len(results) == 3

    def test_get_top_rated_hotels_default(self, service):
        results = service.get_top_rated_hotels("Москва")
        assert len(results) == 5

    def test_rate_hotel_success(self, service):
        result = service.rate_hotel(1, 5.0)
        assert result is True
        hotel = service.get_hotel(1)
        assert hotel.rating == 4.8  # ошибка — не изменился
