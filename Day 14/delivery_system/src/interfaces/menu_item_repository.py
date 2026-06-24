from abc import ABC, abstractmethod
from typing import List, Optional
from src.interfaces.menu_item import MenuItem

class MenuItemRepository(ABC):
    @abstractmethod
    def add(self, item: MenuItem) -> None: pass

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[MenuItem]: pass

    @abstractmethod
    def get_by_restaurant(self, restaurant_id: int) -> List[MenuItem]: pass
