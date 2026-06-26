import pytest
from src.infrastructure.repositories import HotelRepository
from src.core.domain import Hotel, Room
from src.core.exceptions import HotelNotFoundError


class TestHotelRepository:
    def test_add_and_get_by_id(self):
        repo = HotelRepository()
        hotel = Hotel(None, "Test", "Moscow", 4.5)
        saved = repo.add(hotel)
        found = repo.get_by_id(saved.id)
        assert found is not None
        assert found.name == "Test"

    def test_get_all(self):
        repo = HotelRepository()
        hotel1 = Hotel(None, "Test1", "Moscow", 4.0)
        hotel2 = Hotel(None, "Test2", "Moscow", 4.5)
        repo.add(hotel1)
        repo.add(hotel2)
        all_hotels = repo.get_all()
        assert len(all_hotels) == 2

    def test_update_not_found(self):
        repo = HotelRepository()
        hotel = Hotel(999, "Test", "Moscow", 4.5)
        with pytest.raises(HotelNotFoundError):
            repo.update(hotel)

    def test_delete(self):
        repo = HotelRepository()
        hotel = Hotel(None, "Test", "Moscow", 4.5)
        saved = repo.add(hotel)
        assert repo.delete(saved.id) is True
        assert repo.delete(saved.id) is False
