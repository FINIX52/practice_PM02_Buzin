from dataclasses import dataclass

@dataclass
class Restaurant:
    id: int
    name: str
    cuisine_type: str
    lat: float
    lon: float
