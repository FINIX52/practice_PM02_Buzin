def validate_rating(rating: float) -> bool:
    return 0.0 <= rating <= 5.0


def validate_city(city: str) -> bool:
    return bool(city and city.strip())


def validate_hotel_name(name: str) -> bool:
    return bool(name and name.strip())
