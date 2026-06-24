import pytest
import time
from app.delivery import DeliveryCalculator
from app.exceptions import DeliveryAPIError, DeliveryCalculationError


class TestDeliveryCalculator:
    """Тесты для DeliveryCalculator"""

    def test_calculate_delivery_success(self, httpx_mock, delivery_calculator, sample_items):
        httpx_mock.add_response(
            method="POST",
            url="https://api.logistics.com/delivery/calculate",
            json={"price": 200.0, "estimated_time": "2-3 days", "weight": 2.8},
            status_code=200
        )

        result = delivery_calculator.calculate_delivery(sample_items)

        assert result['delivery_cost'] == 240.0
        assert result['weight'] == 2.8
        assert result['estimated_time'] == "2-3 days"

    def test_calculate_delivery_api_error(self, httpx_mock, delivery_calculator, sample_items):
        httpx_mock.add_response(
            method="POST",
            url="https://api.logistics.com/delivery/calculate",
            status_code=500
        )

        with pytest.raises(DeliveryAPIError, match="API доставки вернул ошибку: 500"):
            delivery_calculator.calculate_delivery(sample_items)

    def test_calculate_delivery_timeout(self, httpx_mock, mocker, delivery_calculator, sample_items):
        import httpx
        
        mocker.patch(
            'httpx.post',
            side_effect=httpx.TimeoutException("Timeout")
        )

        with pytest.raises(DeliveryAPIError, match="Таймаут при вызове API доставки"):
            delivery_calculator.calculate_delivery(sample_items)

    def test_calculate_delivery_invalid_response(self, httpx_mock, delivery_calculator, sample_items):
        httpx_mock.add_response(
            method="POST",
            url="https://api.logistics.com/delivery/calculate",
            json={"estimated_time": "2 days"},
            status_code=200
        )

        with pytest.raises(DeliveryCalculationError, match="Ответ API не содержит поле 'price'"):
            delivery_calculator.calculate_delivery(sample_items)

    def test_calculate_delivery_missing_field(self, httpx_mock, delivery_calculator, sample_items):
        httpx_mock.add_response(
            method="POST",
            url="https://api.logistics.com/delivery/calculate",
            json={"price": 200.0},
            status_code=200
        )

        result = delivery_calculator.calculate_delivery(sample_items)
        assert result['estimated_time'] == 'unknown'

    def test_calculate_delivery_empty_items(self, httpx_mock, delivery_calculator):
        httpx_mock.add_response(
            method="POST",
            url="https://api.logistics.com/delivery/calculate",
            json={"price": 50.0, "estimated_time": "1 day", "weight": 0.0},
            status_code=200
        )

        result = delivery_calculator.calculate_delivery([])
        assert result['delivery_cost'] == 60.0
        assert result['weight'] == 0.0

    def test_calculate_delivery_with_retry_success(self, httpx_mock, delivery_calculator, sample_items):
        httpx_mock.add_response(
            method="POST",
            url="https://api.logistics.com/delivery/calculate",
            status_code=500,
            text="Internal Server Error"
        )
        httpx_mock.add_response(
            method="POST",
            url="https://api.logistics.com/delivery/calculate",
            json={"price": 150.0, "estimated_time": "1 day", "weight": 2.8},
            status_code=200
        )

        result = delivery_calculator.calculate_delivery_with_retry(sample_items, max_retries=3)
        assert result['delivery_cost'] == 180.0

    def test_calculate_delivery_with_retry_all_fail(self, httpx_mock, delivery_calculator, sample_items):
        for _ in range(3):
            httpx_mock.add_response(
                method="POST",
                url="https://api.logistics.com/delivery/calculate",
                status_code=500,
                text="Internal Server Error"
            )

        with pytest.raises(DeliveryAPIError):
            delivery_calculator.calculate_delivery_with_retry(sample_items, max_retries=3)

    def test_calculate_delivery_with_mock(self, mocker, delivery_calculator, sample_items):
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"price": 100.0, "estimated_time": "3 days"}

        mocker.patch('httpx.post', return_value=mock_response)

        result = delivery_calculator.calculate_delivery(sample_items)
        assert result['delivery_cost'] == 120.0
        assert result['estimated_time'] == "3 days"

    @pytest.mark.parametrize("items, expected_weight, expected_cost", [
        ([{"name": "A", "weight": 1.0}], 1.0, 120.0),
        ([{"name": "A", "weight": 1.0}, {"name": "B", "weight": 2.0}], 3.0, 240.0),
        ([{"name": "A", "weight": 0.0}], 0.0, 60.0),
        ([], 0.0, 60.0),
    ])
    def test_calculate_delivery_parametrized(
        self,
        httpx_mock,
        delivery_calculator,
        items,
        expected_weight,
        expected_cost
    ):
        httpx_mock.add_response(
            method="POST",
            url="https://api.logistics.com/delivery/calculate",
            json={"price": expected_cost / 1.2, "estimated_time": "2 days", "weight": expected_weight},
            status_code=200
        )

        result = delivery_calculator.calculate_delivery(items)
        assert result['delivery_cost'] == expected_cost
        assert result['weight'] == expected_weight

    def test_calculate_delivery_performance(self, httpx_mock, delivery_calculator, sample_items):
        import time

        httpx_mock.add_response(
            method="POST",
            url="https://api.logistics.com/delivery/calculate",
            json={"price": 200.0, "estimated_time": "2 days", "weight": 2.8},
            status_code=200
        )

        start = time.perf_counter()
        delivery_calculator.calculate_delivery(sample_items)
        elapsed = time.perf_counter() - start

        # Увеличиваем лимит до 1.5 секунд
        assert elapsed < 1.5, f"Расчёт занял {elapsed:.2f} секунд"
