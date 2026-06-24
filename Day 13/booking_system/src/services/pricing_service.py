from datetime import date, timedelta
from typing import Optional, List, Dict
from src.domain.models import Room


class PricingService:
    def __init__(self, seasonal_coefficients: Optional[Dict] = None):
        self.seasonal_coefficients = seasonal_coefficients or {
            1: 1.1, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0,
            6: 1.2, 7: 1.5, 8: 1.5, 9: 1.0, 10: 1.0,
            11: 1.0, 12: 1.3,
        }

    def calculate_price(self, room: Room, check_in: date, check_out: date) -> float:
        nights = (check_out - check_in).days
        if nights <= 0:
            return 0.0

        total = 0.0
        current_date = check_in

        while current_date < check_out:
            month = current_date.month
            coefficient = self.seasonal_coefficients.get(month, 1.0)
            total += room.price_per_night * coefficient
            current_date += timedelta(days=1)  # ← ИСПРАВЛЕНО!

        if nights >= 7:
            total *= 0.95
        if nights >= 14:
            total *= 0.9

        return round(total, 2)

    def calculate_group_price(self, rooms: List[Room], check_in: date, check_out: date) -> float:
        total = sum(self.calculate_price(r, check_in, check_out) for r in rooms)
        if len(rooms) >= 3:
            total *= 0.95
        return round(total, 2)