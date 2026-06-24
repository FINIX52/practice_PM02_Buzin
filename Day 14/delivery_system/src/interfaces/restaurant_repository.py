from abc import ABC, abstractmethod
from typing import List, Optional
from src.interfaces.restaurant import Restaurant

class RestaurantRepository(ABC):
    @abstractmethod
    def add(self, restaurant: Restaurant) -> None: pass

    @abstractmethod
    def get_by_id(self, restaurant_id: int) -> Optional[Restaurant]: pass

    @abstractmethod
    def get_all(self) -> List[Restaurant]: pass
