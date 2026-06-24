import httpx
from typing import Dict, Any, List
from app.exceptions import DeliveryAPIError, DeliveryCalculationError


class DeliveryCalculator:
    """Сервис для расчёта стоимости доставки через внешнее API"""

    def __init__(self, base_url: str = "https://api.logistics.com"):
        self.base_url = base_url
        self.timeout = 30.0

    def calculate_delivery(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_weight = sum(item.get('weight', 0.0) for item in items)
        payload = {"items": items, "total_weight": total_weight}

        try:
            response = httpx.post(
                f"{self.base_url}/delivery/calculate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            if 'price' not in data:
                raise DeliveryCalculationError("Ответ API не содержит поле 'price'")

            delivery_cost = data['price'] * 1.2

            return {
                'delivery_cost': round(delivery_cost, 2),
                'weight': total_weight,
                'estimated_time': data.get('estimated_time', 'unknown')
            }

        except httpx.TimeoutException:
            raise DeliveryAPIError("Таймаут при вызове API доставки")
        except httpx.HTTPStatusError as e:
            raise DeliveryAPIError(f"API доставки вернул ошибку: {e.response.status_code}")
        except DeliveryCalculationError:
            # Пропускаем своё исключение дальше
            raise
        except Exception as e:
            raise DeliveryAPIError(f"Неизвестная ошибка: {str(e)}")

    def calculate_delivery_with_retry(
        self,
        items: List[Dict[str, Any]],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        last_error = None
        for attempt in range(max_retries):
            try:
                return self.calculate_delivery(items)
            except DeliveryAPIError as e:
                last_error = e
                if attempt == max_retries - 1:
                    raise
        raise last_error
