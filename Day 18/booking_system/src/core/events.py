from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class DomainEvent:
    event_type: str
    occurred_at: datetime
    data: dict


@dataclass
class HotelCreatedEvent(DomainEvent):
    def __init__(self, hotel_id: int, name: str):
        super().__init__(
            event_type="hotel_created",
            occurred_at=datetime.now(),
            data={"hotel_id": hotel_id, "name": name}
        )


@dataclass
class HotelRatedEvent(DomainEvent):
    def __init__(self, hotel_id: int, new_rating: float, old_rating: float):
        super().__init__(
            event_type="hotel_rated",
            occurred_at=datetime.now(),
            data={
                "hotel_id": hotel_id,
                "new_rating": new_rating,
                "old_rating": old_rating
            }
        )
