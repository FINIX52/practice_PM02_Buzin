from abc import ABC, abstractmethod
from typing import List, Optional
from src.interfaces.order import Order

class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> None: pass

    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[Order]: pass

    @abstractmethod
    def update_status(self, order_id: int, status: str) -> None: pass
