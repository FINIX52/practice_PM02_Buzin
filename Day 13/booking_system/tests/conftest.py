import pytest
from datetime import date
from src.uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService
from src.services.booking_service import BookingService
from src.services.group_booking_service import GroupBookingService
from src.domain.models import Room


@pytest.fixture
def uow():
    return UnitOfWork()


@pytest.fixture
def pricing_service():
    return PricingService()


@pytest.fixture
def booking_service(uow, pricing_service):
    return BookingService(uow, pricing_service)


@pytest.fixture
def group_service(uow, pricing_service):
    return GroupBookingService(uow, pricing_service)


@pytest.fixture
def setup_room(uow):
    """Создание тестового номера с ценой 100 за ночь"""
    room = Room(id=None, hotel_id=1, number="101", capacity=2, price_per_night=100.0)  # ← ИСПРАВЛЕНО
    return uow.rooms.add(room)


@pytest.fixture
def setup_rooms(uow):
    """Создание нескольких тестовых номеров"""
    rooms = [
        Room(id=None, hotel_id=1, number="101", capacity=2, price_per_night=100.0),
        Room(id=None, hotel_id=1, number="102", capacity=2, price_per_night=120.0),
        Room(id=None, hotel_id=1, number="103", capacity=4, price_per_night=150.0),
        Room(id=None, hotel_id=1, number="104", capacity=2, price_per_night=110.0),
    ]
    for room in rooms:
        uow.rooms.add(room)
    return rooms