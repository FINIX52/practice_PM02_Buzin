import pytest
from src.presentation.api import HotelAPI
from src.application.services import HotelService, create_test_data
from src.application.dto import SearchHotelsDTO


@pytest.fixture
def api():
    service = create_test_data()
    return HotelAPI(service)


class TestHotelAPI:
    def test_add_hotel(self, api):
        result = api.add_hotel("API Hotel", "Москва", 4.0)
        assert result is True

    def test_search_by_city(self, api):
        results = api.search(city="Москва")
        assert len(results) == 4

    def test_search_by_min_rating(self, api):
        results = api.search(min_rating=4.0)
        assert len(results) == 3
