from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx

from app.models import Order, OrderItem
from app.exceptions import EntityNotFoundException, DeliveryCalculationException


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, order_data: Dict[str, Any]) -> Order:
        """Создать заказ с позициями"""
        items_data = order_data.pop("items", [])
        
        # ВАЛИДАЦИЯ: количество должно быть положительным
        for item_data in items_data:
            if item_data.get("quantity", 0) <= 0:
                raise ValueError(f"Quantity must be positive, got {item_data.get('quantity')}")
        
        order = Order(**order_data)
        self.session.add(order)
        self.session.flush()

        for item_data in items_data:
            item = OrderItem(order_id=order.id, **item_data)
            self.session.add(item)

        self.session.commit()
        self.session.refresh(order)
        return order

    def find_by_id(self, order_id: int) -> Optional[Order]:
        return self.session.query(Order).filter(Order.id == order_id).first()

    def find_all_by_status(self, status: str) -> List[Order]:
        return self.session.query(Order).filter(Order.status == status).all()

    def update_status(self, order_id: int, new_status: str) -> Order:
        order = self.find_by_id(order_id)
        if not order:
            raise EntityNotFoundException(f"Order with id {order_id} not found")
        order.status = new_status
        self.session.commit()
        self.session.refresh(order)
        return order

    def delete(self, order_id: int) -> None:
        order = self.find_by_id(order_id)
        if not order:
            raise EntityNotFoundException(f"Order with id {order_id} not found")
        self.session.delete(order)
        self.session.commit()

    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        return self.session.query(Order).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        ).all()

    def get_total_amount_for_order(self, order_id: int) -> float:
        result = self.session.query(func.sum(OrderItem.quantity * OrderItem.price)).filter(
            OrderItem.order_id == order_id
        ).scalar()
        return result or 0.0

    def calculate_delivery_cost(self, order_id: int) -> float:
        order = self.find_by_id(order_id)
        if not order:
            raise EntityNotFoundException(f"Order with id {order_id} not found")

        total_weight = sum(item.quantity * 0.5 for item in order.items)

        try:
            response = httpx.post(
                "https://api.delivery.com/calculate",
                json={
                    "address": order.delivery_address,
                    "weight": total_weight
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("cost", 0.0)

        except httpx.HTTPStatusError as e:
            raise DeliveryCalculationException(f"Delivery API error: {e.response.status_code}")
        except httpx.TimeoutException:
            raise DeliveryCalculationException("Delivery API timeout")
        except Exception as e:
            raise DeliveryCalculationException(f"Delivery API error: {str(e)}")
