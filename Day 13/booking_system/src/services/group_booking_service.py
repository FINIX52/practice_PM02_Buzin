from datetime import date, datetime
from typing import List, Optional
from src.domain.models import Booking, BookingStatus, GroupBooking, Room
from src.domain.exceptions import (
    RoomNotFoundError, BookingConflictError,
    InvalidDatesError, GroupBookingError
)
from src.dto.booking_dto import GroupBookingCreateDTO, GroupBookingResponseDTO
from src.uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService


class GroupBookingService:
    def __init__(self, uow: UnitOfWork, pricing_service: PricingService):
        self.uow = uow
        self.pricing_service = pricing_service
        self.booking_repo = uow.bookings
        self.room_repo = uow.rooms
        self.group_booking_repo = uow.group_bookings

    def create_group_booking(self, dto: GroupBookingCreateDTO) -> GroupBookingResponseDTO:
        if dto.check_out <= dto.check_in:
            raise InvalidDatesError("Дата выезда должна быть позже даты заезда")

        rooms = []
        for room_id in dto.room_ids:
            room = self.room_repo.get_by_id(room_id)
            if not room or not room.is_active:
                raise RoomNotFoundError(f"Номер {room_id} не найден или не активен")
            rooms.append(room)

        hotel_id = rooms[0].hotel_id
        for room in rooms:
            if room.hotel_id != hotel_id:
                raise GroupBookingError("Все номера должны быть в одном отеле")

        unavailable = []
        for room in rooms:
            existing = self.booking_repo.get_by_room_and_dates(
                room.id, dto.check_in, dto.check_out
            )
            if existing:
                unavailable.append({'room_id': room.id, 'conflicts': [b.id for b in existing]})

        if unavailable:
            self.uow.rollback()
            raise BookingConflictError(
                "Некоторые номера уже забронированы",
                details={"unavailable_rooms": unavailable}
            )

        total_price = self.pricing_service.calculate_group_price(
            rooms, dto.check_in, dto.check_out
        )

        group = GroupBooking(
            id=None,
            group_name=dto.group_name,
            contact_email=dto.contact_email,
            check_in=dto.check_in,
            check_out=dto.check_out,
            total_price=total_price,
            status=BookingStatus.PENDING,
            booking_ids=[]
        )
        saved_group = self.group_booking_repo.add(group)

        for room in rooms:
            booking = Booking(
                id=None,
                room_id=room.id,
                guest_name=dto.group_name,
                guest_email=dto.contact_email,
                check_in=dto.check_in,
                check_out=dto.check_out,
                total_price=self.pricing_service.calculate_price(
                    room, dto.check_in, dto.check_out
                ),
                status=BookingStatus.PENDING,
                group_id=saved_group.id
            )
            saved = self.booking_repo.add(booking)
            saved_group.booking_ids.append(saved.id)

        self.group_booking_repo.update(saved_group)
        self.uow.commit()

        return GroupBookingResponseDTO(
            id=saved_group.id,
            group_name=saved_group.group_name,
            contact_email=saved_group.contact_email,
            check_in=saved_group.check_in,
            check_out=saved_group.check_out,
            total_price=saved_group.total_price,
            status=saved_group.status.value,
            booking_ids=saved_group.booking_ids,
            created_at=saved_group.created_at
        )

    def cancel_group_booking(self, group_id: int) -> bool:
        group = self.group_booking_repo.get_by_id(group_id)
        if not group:
            raise GroupBookingError(f"Групповое бронирование {group_id} не найдено")
        if group.status == BookingStatus.CANCELLED:
            return True
        if group.status in (BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT):
            raise GroupBookingError("Нельзя отменить активное бронирование")

        for booking_id in group.booking_ids:
            booking = self.booking_repo.get_by_id(booking_id)
            if booking and booking.status != BookingStatus.CANCELLED:
                booking.status = BookingStatus.CANCELLED
                booking.cancelled_at = datetime.now()
                self.booking_repo.update(booking)

        group.status = BookingStatus.CANCELLED
        group.cancelled_at = datetime.now()
        self.group_booking_repo.update(group)
        self.uow.commit()
        return True

    def confirm_group_booking(self, group_id: int) -> bool:
        group = self.group_booking_repo.get_by_id(group_id)
        if not group:
            raise GroupBookingError(f"Групповое бронирование {group_id} не найдено")
        if group.status != BookingStatus.PENDING:
            raise GroupBookingError("Нельзя подтвердить неподтверждённое бронирование")

        for booking_id in group.booking_ids:
            booking = self.booking_repo.get_by_id(booking_id)
            if booking:
                booking.status = BookingStatus.CONFIRMED
                self.booking_repo.update(booking)

        group.status = BookingStatus.CONFIRMED
        self.group_booking_repo.update(group)
        self.uow.commit()
        return True

    def get_group_booking(self, group_id: int) -> Optional[GroupBookingResponseDTO]:
        group = self.group_booking_repo.get_by_id(group_id)
        if not group:
            return None
        return GroupBookingResponseDTO(
            id=group.id,
            group_name=group.group_name,
            contact_email=group.contact_email,
            check_in=group.check_in,
            check_out=group.check_out,
            total_price=group.total_price,
            status=group.status.value,
            booking_ids=group.booking_ids,
            created_at=group.created_at
        )

    def check_availability_for_group(
        self,
        room_ids: List[int],
        check_in: date,
        check_out: date
    ) -> dict:
        result = {'available': [], 'unavailable': [], 'all_available': True}
        for room_id in room_ids:
            room = self.room_repo.get_by_id(room_id)
            if not room or not room.is_active:
                result['unavailable'].append({'room_id': room_id, 'reason': 'not_available'})
                result['all_available'] = False
                continue
            existing = self.booking_repo.get_by_room_and_dates(room_id, check_in, check_out)
            if existing:
                result['unavailable'].append({
                    'room_id': room_id,
                    'room_number': room.number,
                    'reason': 'booked',
                    'conflicts': [b.id for b in existing]
                })
                result['all_available'] = False
            else:
                result['available'].append({
                    'room_id': room_id,
                    'room_number': room.number,
                    'capacity': room.capacity,
                    'price_per_night': room.price_per_night
                })
        return result
