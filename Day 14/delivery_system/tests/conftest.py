import pytest
from unittest.mock import Mock
from src.interfaces.restaurant_repository import RestaurantRepository
from src.interfaces.menu_item_repository import MenuItemRepository
from src.interfaces.order_repository import OrderRepository
from src.delivery_service import DeliveryService

@pytest.fixture
def mock_repos():
    return {
        "restaurant": Mock(spec=RestaurantRepository),
        "menu": Mock(spec=MenuItemRepository),
        "order": Mock(spec=OrderRepository)
    }

@pytest.fixture
def service(mock_repos):
    return DeliveryService(
        rest_repo=mock_repos["restaurant"],
        menu_repo=mock_repos["menu"],
        order_repo=mock_repos["order"]
    )
