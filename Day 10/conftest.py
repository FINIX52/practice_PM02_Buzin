import pytest
from datetime import datetime, timedelta
from fake_validator import FakeValidator


@pytest.fixture
def validator():
    return FakeValidator(chaos_mode=False)


@pytest.fixture
def chaos_validator():
    return FakeValidator(chaos_mode=True)


def create_base_order(
    total_amount: float = 5000,
    is_new: bool = False,
    total_items: int = 1,
    has_alcohol: bool = False,
    age_verified: bool = True,
    order_hour: int = 12,
    email_changed_hours_ago: int = 24,
    delivery_country: str = "RU",
    user_country: str = "RU"
) -> dict:
    now = datetime.now()
    items = []
    if has_alcohol:
        items.append({"name": "Виски", "category": "Alcohol", "price": 5000, "quantity": 1})
    if total_items > 0:
        items.append({"name": "Товар", "category": "Food", "price": 100, "quantity": max(1, total_items)})

    return {
        "order_id": "ORD-TEST",
        "user_id": "USR-TEST",
        "created_at": (now - timedelta(days=1)).isoformat(),
        "total_amount": total_amount,
        "items": items,
        "user_info": {
            "is_new": is_new,
            "age_verified": age_verified,
            "email_changed_at": (now - timedelta(hours=email_changed_hours_ago)).isoformat(),
            "country": user_country
        },
        "delivery_country": delivery_country,
        "order_time": now.replace(hour=order_hour, minute=0, second=0, microsecond=0).isoformat()
    }