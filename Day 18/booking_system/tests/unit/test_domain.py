import pytest
from src.core.domain import Hotel, Room


class TestHotel:
    def test_hotel_creation(self):
        hotel = Hotel(1, "Test Hotel", "Москва", 4.5)
        assert hotel.id == 1
        assert hotel.name == "Test Hotel"
        assert hotel.city == "Москва"
        assert hotel.rating == 4.5

    def test_add_room(self):
        hotel = Hotel(1, "Test Hotel", "Москва", 4.5)
        room = Room(101, "standard", 5000, 2)
        result = hotel.add_room(room)
        assert result is True
        assert len(hotel.rooms) == 1

    def test_get_available_rooms(self):
        hotel = Hotel(1, "Test Hotel", "Москва", 4.5)
        room = Room(101, "standard", 5000, 2)
        hotel.add_room(room)
        rooms = hotel.get_available_rooms()
        assert len(rooms) == 1
