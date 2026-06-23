import pytest
from datetime import date
from src.services.booking_service import BookingService
from src.services.pricing_service import PricingService
from src.uow.unit_of_work import UnitOfWork
from src.dto.booking_dto import BookingCreateDTO
from src.domain.models import Room, BookingStatus
from src.domain.exceptions import RoomNotFoundError, BookingConflictError


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
def setup_room(uow):
    room = Room(id=None, hotel_id=1, number="101", capacity=2, price_per_night=100.0)
    return uow.rooms.add(room)


class TestBookingService:

    def test_create_booking_success(self, booking_service, uow, setup_room):
        dto = BookingCreateDTO(
            room_id=setup_room.id,
            guest_name="John Doe",
            guest_email="john@example.com",
            check_in=date(2026, 7, 15),
            check_out=date(2026, 7, 20)
        )

        result = booking_service.create(dto)

        assert result.id is not None
        assert result.room_id == setup_room.id
        assert result.guest_name == "John Doe"
        assert result.total_price > 0
        assert result.status == "pending"

    def test_create_booking_room_not_found(self, booking_service):
        dto = BookingCreateDTO(
            room_id=999,
            guest_name="Jane Doe",
            guest_email="jane@example.com",
            check_in=date(2026, 7, 15),
            check_out=date(2026, 7, 20)
        )

        with pytest.raises(RoomNotFoundError, match="Номер 999 не найден"):
            booking_service.create(dto)

    def test_create_booking_conflict(self, booking_service, uow, setup_room):
        dto1 = BookingCreateDTO(
            room_id=setup_room.id,
            guest_name="First Guest",
            guest_email="first@example.com",
            check_in=date(2026, 7, 15),
            check_out=date(2026, 7, 20)
        )
        booking_service.create(dto1)

        dto2 = BookingCreateDTO(
            room_id=setup_room.id,
            guest_name="Second Guest",
            guest_email="second@example.com",
            check_in=date(2026, 7, 16),
            check_out=date(2026, 7, 18)
        )

        with pytest.raises(BookingConflictError, match="уже забронирован"):
            booking_service.create(dto2)

    def test_create_booking_invalid_dates(self, booking_service, setup_room):
        """Тест: неверные даты (выезд раньше заезда)"""
        with pytest.raises(ValueError, match="Дата выезда должна быть позже"):
            BookingCreateDTO(
                room_id=setup_room.id,
                guest_name="Test Guest",
                guest_email="test@example.com",
                check_in=date(2026, 7, 20),
                check_out=date(2026, 7, 15)
            )

    def test_create_booking_too_long(self, booking_service, setup_room):
        """Тест: бронирование дольше 30 дней"""
        with pytest.raises(ValueError, match="не может превышать 30 дней"):
            BookingCreateDTO(
                room_id=setup_room.id,
                guest_name="Test Guest",
                guest_email="test@example.com",
                check_in=date(2026, 7, 1),
                check_out=date(2026, 8, 5)  # 35 дней
            )

    def test_pricing_calculation(self, booking_service, uow, setup_room):
        """Тест: проверка расчёта цены"""
        dto = BookingCreateDTO(
            room_id=setup_room.id,
            guest_name="Test Guest",
            guest_email="test@example.com",
            check_in=date(2026, 7, 10),
            check_out=date(2026, 7, 13)  # 3 ночи
        )

        result = booking_service.create(dto)
        # 100 * 1.5 (июль) * 3 = 450
        assert result.total_price == 450.0

    def test_cancel_booking_success(self, booking_service, uow, setup_room):
        dto = BookingCreateDTO(
            room_id=setup_room.id,
            guest_name="Test Guest",
            guest_email="test@example.com",
            check_in=date(2026, 8, 1),
            check_out=date(2026, 8, 5)
        )
        result = booking_service.create(dto)

        canceled = booking_service.cancel(result.id)
        assert canceled is True

        booking = uow.bookings.get_by_id(result.id)
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancelled_at is not None

    def test_cancel_booking_not_found(self, booking_service):
        with pytest.raises(Exception, match="не найдено"):
            booking_service.cancel(999)
