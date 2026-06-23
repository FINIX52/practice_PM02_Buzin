from contextlib import contextmanager
from src.repositories.booking_repo import BookingRepository
from src.repositories.group_booking_repo import GroupBookingRepository
from src.repositories.hotel_repo import HotelRepository
from src.repositories.room_repo import RoomRepository


class UnitOfWork:
    def __init__(self):
        self._hotel_repo = HotelRepository()
        self._room_repo = RoomRepository()
        self._booking_repo = BookingRepository()
        self._group_booking_repo = GroupBookingRepository()
        self._committed = False
        self._rolled_back = False

    @property
    def hotels(self) -> HotelRepository:
        return self._hotel_repo

    @property
    def rooms(self) -> RoomRepository:
        return self._room_repo

    @property
    def bookings(self) -> BookingRepository:
        return self._booking_repo

    @property
    def group_bookings(self) -> GroupBookingRepository:
        return self._group_booking_repo

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        self._rolled_back = True

    @contextmanager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        elif not self._committed and not self._rolled_back:
            self.commit()
