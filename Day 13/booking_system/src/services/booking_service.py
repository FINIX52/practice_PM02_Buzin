from datetime import date, datetime
from typing import List, Optional, Dict, Any
from src.domain.models import Booking, BookingStatus, Room
from src.domain.exceptions import (
    RoomNotFoundError,
    BookingConflictError,
    BookingNotFoundError,
    InvalidDatesError,
    DomainError
)
from src.dto.booking_dto import BookingCreateDTO, BookingResponseDTO
from src.uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService


class BookingService:
    def __init__(self, uow: UnitOfWork, pricing_service: PricingService):
        self.uow = uow
        self.pricing_service = pricing_service
        self.booking_repo = uow.bookings
        self.room_repo = uow.rooms

    def create(self, dto: BookingCreateDTO) -> BookingResponseDTO:
        room = self.room_repo.get_by_id(dto.room_id)
        if not room or not room.is_active:
            raise RoomNotFoundError(f"Номер {dto.room_id} не найден или не активен")

        existing = self.booking_repo.get_by_room_and_dates(
            dto.room_id, dto.check_in, dto.check_out
        )
        if existing:
            raise BookingConflictError(
                f"Номер {dto.room_id} уже забронирован",
                details={"conflicting_bookings": [b.id for b in existing]}
            )

        total_price = self.pricing_service.calculate_price(
            room, dto.check_in, dto.check_out
        )

        booking = Booking(
            id=None,
            room_id=dto.room_id,
            guest_name=dto.guest_name,
            guest_email=dto.guest_email,
            check_in=dto.check_in,
            check_out=dto.check_out,
            total_price=total_price,
            status=BookingStatus.PENDING
        )

        saved = self.booking_repo.add(booking)
        self.uow.commit()

        return BookingResponseDTO(
            id=saved.id,
            room_id=saved.room_id,
            guest_name=saved.guest_name,
            check_in=saved.check_in,
            check_out=saved.check_out,
            total_price=saved.total_price,
            status=saved.status.value,
            created_at=saved.created_at
        )

    def cancel(self, booking_id: int) -> bool:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")
        if booking.status in (BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT):
            raise DomainError(f"Нельзя отменить бронирование в статусе {booking.status.value}")
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now()
        self.booking_repo.update(booking)
        self.uow.commit()
        return True