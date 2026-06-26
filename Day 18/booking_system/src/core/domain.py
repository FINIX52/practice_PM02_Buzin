from typing import List, Dict, Any, Optional


class Room:
    def __init__(self, room_id: int, room_type: str, price: float, capacity: int):
        self.id = room_id
        self.type = room_type
        self.price = price
        self.capacity = capacity
        self.is_available = True


class Hotel:
    def __init__(self, hotel_id: int, name: str, city: str, rating: float = 0.0):
        self.id = hotel_id
        self.name = name
        self.city = city
        self.rating = rating
        self.rooms: List[Room] = []

    def add_room(self, room: Room) -> bool:
        self.rooms.append(room)
        return True

    def get_available_rooms(self) -> List[Room]:
        return [room for room in self.rooms if room.is_available]
