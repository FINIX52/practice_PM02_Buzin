import pytest
from src.utils.validators import validate_rating, validate_city, validate_hotel_name


class TestValidators:
    @pytest.mark.parametrize("rating, expected", [
        (0.0, True),
        (2.5, True),
        (5.0, True),
        (-0.1, False),
        (5.1, False),
    ])
    def test_validate_rating(self, rating, expected):
        assert validate_rating(rating) == expected

    @pytest.mark.parametrize("city, expected", [
        ("Москва", True),
        ("", False),
        (" ", False),
        ("  Санкт-Петербург  ", True),
    ])
    def test_validate_city(self, city, expected):
        assert validate_city(city) == expected

    def test_validate_hotel_name(self):
        assert validate_hotel_name("Grand Hotel") is True
        assert validate_hotel_name("") is False
        assert validate_hotel_name("   ") is False
