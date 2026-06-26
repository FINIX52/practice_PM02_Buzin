import httpx
from typing import Dict, Any


class ExternalRatingAPI:
    def __init__(self, base_url: str = "https://api.ratings.com"):
        self.base_url = base_url

    def fetch_rating(self, hotel_id: int) -> float:
        try:
            response = httpx.get(
                f"{self.base_url}/hotels/{hotel_id}/rating",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("rating", 0.0)
        except Exception:
            return 0.0
