import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.delivery import DeliveryCalculator


@pytest.fixture
def delivery_calculator():
    return DeliveryCalculator()


@pytest.fixture
def sample_items():
    return [
        {"name": "Книга", "weight": 0.5},
        {"name": "Телефон", "weight": 0.3},
        {"name": "Ноутбук", "weight": 2.0},
    ]