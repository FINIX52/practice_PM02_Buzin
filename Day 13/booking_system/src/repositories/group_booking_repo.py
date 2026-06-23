from typing import List, Optional
from src.domain.models import GroupBooking, BookingStatus
from src.repositories.base import BaseRepository


class GroupBookingRepository(BaseRepository[GroupBooking]):
    def __init__(self):
        self._storage: dict[int, GroupBooking] = {}
        self._next_id = 1

    def get_by_id(self, id: int) -> Optional[GroupBooking]:
        return self._storage.get(id)

    def get_all(self, **filters) -> List[GroupBooking]:
        result = list(self._storage.values())
        if 'status' in filters:
            result = [g for g in result if g.status == filters['status']]
        if 'contact_email' in filters:
            result = [g for g in result if g.contact_email == filters['contact_email']]
        return result

    def add(self, group_booking: GroupBooking) -> GroupBooking:
        group_booking.id = self._next_id
        self._storage[group_booking.id] = group_booking
        self._next_id += 1
        return group_booking

    def update(self, group_booking: GroupBooking) -> GroupBooking:
        if group_booking.id not in self._storage:
            raise ValueError(f"GroupBooking with id {group_booking.id} not found")
        self._storage[group_booking.id] = group_booking
        return group_booking

    def delete(self, id: int) -> bool:
        if id in self._storage:
            del self._storage[id]
            return True
        return False
