import math
from typing import List, Dict
from src.interfaces.restaurant_repository import RestaurantRepository
from src.interfaces.menu_item_repository import MenuItemRepository
from src.interfaces.order_repository import OrderRepository
from src.interfaces.order import Order
from src.exceptions import NotFoundError, ValidationError

class DeliveryService:
    def __init__(self, rest_repo: RestaurantRepository, menu_repo: MenuItemRepository, order_repo: OrderRepository):
        self.rest_repo = rest_repo
        self.menu_repo = menu_repo
        self.order_repo = order_repo

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

    def place_order(self, order_id: int, restaurant_id: int, items_data: List[Dict], user_lat: float, user_lon: float) -> Order:
        restaurant = self.rest_repo.get_by_id(restaurant_id)
        if not restaurant:
            raise NotFoundError(f"Ресторан {restaurant_id} не найден")

        if not items_data:
            raise ValidationError("Заказ не может быть пустым")

        total_menu_price = 0.0
        for entry in items_data:
            item = self.menu_repo.get_by_id(entry["item_id"])
            if not item or item.restaurant_id != restaurant_id:
                raise NotFoundError(f"Блюдо {entry['item_id']} не найдено в этом ресторане")
            if not item.is_available:
                raise ValidationError(f"Блюдо {item.name} сейчас недоступно")
            if entry["quantity"] <= 0:
                raise ValidationError("Количество должно быть больше 0")
            
            total_menu_price += item.price * entry["quantity"]

        distance = self.calculate_distance(restaurant.lat, restaurant.lon, user_lat, user_lon)
        delivery_cost = distance * 10.0
        final_price = total_menu_price + delivery_cost

        new_order = Order(
            id=order_id,
            restaurant_id=restaurant_id,
            items=items_data,
            status="Placed",
            total_price=final_price,
            delivery_lat=user_lat,
            delivery_lon=user_lon
        )
        self.order_repo.add(new_order)
        return new_order

    def update_order_status(self, order_id: int, new_status: str) -> None:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Заказ {order_id} не найден")
        
        valid_statuses = ["Placed", "Prepared", "Delivered"]
        if new_status not in valid_statuses:
            raise ValidationError(f"Недопустимый статус заказа: {new_status}")
            
        self.order_repo.update_status(order_id, new_status)
