import pytest
from datetime import datetime, timedelta
from app.exceptions import EntityNotFoundException, DeliveryCalculationException
from app.models import Order, OrderItem


class TestOrderRepository:
    """Интеграционные тесты для OrderRepository"""

    def test_create_order(self, repo, sample_order_data):
        order = repo.create(sample_order_data)
        assert order.id is not None
        assert order.customer_name == "Иван Петров"
        assert len(order.items) == 2

    def test_find_by_id_success(self, repo, sample_order_data):
        order = repo.create(sample_order_data)
        found = repo.find_by_id(order.id)
        assert found is not None
        assert found.id == order.id

    def test_find_by_id_not_found(self, repo):
        result = repo.find_by_id(999)
        assert result is None

    @pytest.mark.parametrize("status", ["PENDING", "PAID", "SHIPPED", "CANCELLED"])
    def test_find_all_by_status(self, repo, sample_order_data, status):
        order1 = repo.create(sample_order_data)
        repo.update_status(order1.id, "PENDING")
        order2 = repo.create(sample_order_data)
        repo.update_status(order2.id, "PAID")
        order3 = repo.create(sample_order_data)
        repo.update_status(order3.id, "SHIPPED")

        results = repo.find_all_by_status(status)
        for result in results:
            assert result.status == status

    def test_update_status_success(self, repo, sample_order_data):
        order = repo.create(sample_order_data)
        assert order.status == "PENDING"
        updated = repo.update_status(order.id, "PAID")
        assert updated.status == "PAID"

    def test_update_status_not_found(self, repo):
        with pytest.raises(EntityNotFoundException, match="Order with id 999 not found"):
            repo.update_status(999, "PAID")

    def test_delete_order(self, repo, sample_order_data):
        order = repo.create(sample_order_data)
        order_id = order.id
        assert repo.find_by_id(order_id) is not None
        repo.delete(order_id)
        assert repo.find_by_id(order_id) is None

    def test_delete_order_not_found(self, repo):
        with pytest.raises(EntityNotFoundException, match="Order with id 999 not found"):
            repo.delete(999)

    def test_find_by_date_range(self, repo, sample_order_data):
        now = datetime.now()
        order1 = repo.create(sample_order_data)
        order2 = repo.create(sample_order_data)
        
        # Меняем даты через БД
        session = repo.session
        order1.created_at = now - timedelta(days=5)
        order2.created_at = now + timedelta(days=5)
        session.commit()

        start_date = now - timedelta(days=10)
        end_date = now + timedelta(days=10)
        results = repo.find_by_date_range(start_date, end_date)
        assert len(results) >= 2

    def test_get_total_amount(self, repo, sample_order_data):
        order = repo.create(sample_order_data)
        total = repo.get_total_amount_for_order(order.id)
        assert total == 1500.0

    def test_transaction_rollback(self, repo, sample_order_data):
        """Тест: откат транзакции при ошибке"""
        invalid_data = sample_order_data.copy()
        invalid_data["items"] = [
            {"product_name": "Bad Item", "quantity": -5, "price": 100.0}
        ]

        with pytest.raises(ValueError, match="Quantity must be positive"):
            repo.create(invalid_data)

    def test_calculate_delivery_success(self, httpx_mock, repo, sample_order_data):
        order = repo.create(sample_order_data)
        httpx_mock.add_response(
            method="POST",
            url="https://api.delivery.com/calculate",
            json={"cost": 350.0},
            status_code=200
        )
        cost = repo.calculate_delivery_cost(order.id)
        assert cost == 350.0

    def test_calculate_delivery_error(self, httpx_mock, repo, sample_order_data):
        order = repo.create(sample_order_data)
        httpx_mock.add_response(
            method="POST",
            url="https://api.delivery.com/calculate",
            status_code=500
        )
        with pytest.raises(DeliveryCalculationException, match="Delivery API error: 500"):
            repo.calculate_delivery_cost(order.id)

    def test_calculate_delivery_not_found(self, repo):
        with pytest.raises(EntityNotFoundException, match="Order with id 999 not found"):
            repo.calculate_delivery_cost(999)
