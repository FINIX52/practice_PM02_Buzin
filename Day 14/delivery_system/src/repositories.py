from typing import List, Optional
from src.interfaces.restaurant import Restaurant
from src.interfaces.menu_item import MenuItem
from src.interfaces.order import Order
from src.interfaces.restaurant_repository import RestaurantRepository
from src.interfaces.menu_item_repository import MenuItemRepository
from src.interfaces.order_repository import OrderRepository

class InMemoryRestaurantRepository(RestaurantRepository):
    def __init__(self):
        self._restaurants = {}

    def add(self, restaurant: Restaurant) -> None:
        self._restaurants[restaurant.id] = restaurant

    def get_by_id(self, restaurant_id: int) -> Optional[Restaurant]:
        return self._restaurants.get(restaurant_id)

    def get_all(self) -> List[Restaurant]:
        return list(self._restaurants.values())

class InMemoryMenuItemRepository(MenuItemRepository):
    def __init__(self):
        self._items = {}

    def add(self, item: MenuItem) -> None:
        self._items[item.id] = item

    def get_by_id(self, item_id: int) -> Optional[MenuItem]:
        return self._items.get(item_id)

    def get_by_restaurant(self, restaurant_id: int) -> List[MenuItem]:
        return [item for item in self._items.values() if item.restaurant_id == restaurant_id]

class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders = {}

    def add(self, order: Order) -> None:
        self._orders[order.id] = order

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self._orders.get(order_id)

    def update_status(self, order_id: int, status: str) -> None:
        if order_id in self._orders:
            self._orders[order_id].status = status
