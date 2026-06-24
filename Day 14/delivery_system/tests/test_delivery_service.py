import pytest
from src.interfaces.restaurant import Restaurant
from src.interfaces.menu_item import MenuItem
from src.exceptions import NotFoundError, ValidationError

def test_place_order_success(service, mock_repos):
    mock_repos["restaurant"].get_by_id.return_value = Restaurant(1, "Бургерная", "Фастфуд", 55.0, 37.0)
    mock_repos["menu"].get_by_id.return_value = MenuItem(10, 1, "Бургер классик", 250.0, True)

    order = service.place_order(
        order_id=100,
        restaurant_id=1,
        items_data=[{"item_id": 10, "quantity": 2}],
        user_lat=55.0,
        user_lon=37.0
    )

    assert order.status == "Placed"
    assert order.total_price == 500.0
    mock_repos["order"].add.assert_called_once()

def test_place_order_restaurant_not_found(service, mock_repos):
    mock_repos["restaurant"].get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.place_order(100, 999, [{"item_id": 1, "quantity": 1}], 55.0, 37.0)

def test_place_order_item_unavailable(service, mock_repos):
    mock_repos["restaurant"].get_by_id.return_value = Restaurant(1, "Пицца", "Итальянская", 55.0, 37.0)
    mock_repos["menu"].get_by_id.return_value = MenuItem(10, 1, "Маргарита", 400.0, False)

    with pytest.raises(ValidationError):
        service.place_order(100, 1, [{"item_id": 10, "quantity": 1}], 55.0, 37.0)
