from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel
import random


class OrderItem(BaseModel):
    name: str
    category: str
    price: float
    quantity: int


class UserInfo(BaseModel):
    is_new: bool
    age_verified: bool
    email_changed_at: datetime
    country: str


class Order(BaseModel):
    order_id: str
    user_id: str
    created_at: datetime
    total_amount: float
    items: List[OrderItem]
    user_info: UserInfo
    delivery_country: str
    order_time: datetime


class FakeValidator:
    def __init__(self, chaos_mode: bool = False):
        self.chaos_mode = chaos_mode

    def validate_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.chaos_mode and random.random() < 0.05:
            return {
                "valid": random.choice([True, False]),
                "reasons": ["CHAOS_MODE_TRIGGERED"],
                "risk_score": random.random()
            }

        try:
            order = Order(**order_data)
        except Exception as e:
            return {
                "valid": False,
                "reasons": [f"Invalid input: {str(e)}"],
                "risk_score": 0.0
            }

        reasons = []
        risk_score = 0.0

        if not (0 < order.total_amount < 1_000_000):
            reasons.append("Сумма заказа должна быть > 0 и < 1_000_000")

        if order.user_info.is_new and order.total_amount > 15000:
            reasons.append("Новый пользователь → сумма не более 15_000")

        total_items = sum(item.quantity for item in order.items)
        if total_items > 50:
            reasons.append("Количество позиций не должно превышать 50")

        has_alcohol = any(item.category == "Alcohol" for item in order.items)
        if has_alcohol:
            if not order.user_info.age_verified:
                reasons.append("Для алкоголя требуется age_verified = True")
            hour = order.order_time.hour
            if not (8 <= hour <= 23):
                reasons.append("Алкоголь можно заказывать только с 08:00 до 23:00")

        if order.total_amount > 100_000:
            risk_score = max(risk_score, 0.9)

        if (datetime.now() - order.user_info.email_changed_at).total_seconds() < 3600:
            risk_score = min(1.0, risk_score + 0.2)

        if order.delivery_country != order.user_info.country:
            risk_score = min(1.0, risk_score + 0.3)

        return {
            "valid": len(reasons) == 0,
            "reasons": reasons,
            "risk_score": risk_score
        }
