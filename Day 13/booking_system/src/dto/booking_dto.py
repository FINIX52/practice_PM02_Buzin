from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List


class BookingCreateDTO(BaseModel):
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date

    @field_validator('check_out')
    @classmethod
    def validate_dates(cls, v, info):
        check_in = info.data.get('check_in')
        if check_in and v <= check_in:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        if check_in and (v - check_in).days > 30:
            raise ValueError('Бронирование не может превышать 30 дней')
        return v


class BookingResponseDTO(BaseModel):
    id: int
    room_id: int
    guest_name: str
    check_in: date
    check_out: date
    total_price: float
    status: str
    created_at: datetime


class GroupBookingCreateDTO(BaseModel):
    group_name: str
    contact_email: str
    room_ids: List[int]
    check_in: date
    check_out: date

    @field_validator('check_out')
    @classmethod
    def validate_dates(cls, v, info):
        check_in = info.data.get('check_in')
        if check_in and v <= check_in:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        if check_in and (v - check_in).days > 30:
            raise ValueError('Бронирование не может превышать 30 дней')
        return v

    @field_validator('room_ids')
    @classmethod
    def validate_room_ids(cls, v):
        if not v:
            raise ValueError('Должен быть указан хотя бы один номер')
        if len(v) != len(set(v)):
            raise ValueError('Номера не должны повторяться')
        return v


class GroupBookingResponseDTO(BaseModel):
    id: int
    group_name: str
    contact_email: str
    check_in: date
    check_out: date
    total_price: float
    status: str
    booking_ids: List[int]
    created_at: datetime
