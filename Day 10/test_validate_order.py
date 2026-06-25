import pytest
from datetime import datetime, timedelta
from fake_validator import FakeValidator
from conftest import create_base_order


class TestRules:
    @pytest.mark.parametrize("total_amount, expected_valid", [
        (1, True), (0, False), (999999, True), (1000000, False),
    ])
    def test_rule_1_total_amount(self, validator, total_amount, expected_valid):
        order = create_base_order(total_amount=total_amount)
        result = validator.validate_order(order)
        assert result["valid"] == expected_valid

    @pytest.mark.parametrize("is_new, total_amount, expected_valid", [
        (True, 15000, True), (True, 15001, False), (False, 15000, True),
    ])
    def test_rule_2_new_user(self, validator, is_new, total_amount, expected_valid):
        order = create_base_order(total_amount=total_amount, is_new=is_new)
        result = validator.validate_order(order)
        assert result["valid"] == expected_valid

    @pytest.mark.parametrize("total_items, expected_valid", [
        (50, True), (51, False),
    ])
    def test_rule_3_items_count(self, validator, total_items, expected_valid):
        order = create_base_order(total_items=total_items)
        result = validator.validate_order(order)
        assert result["valid"] == expected_valid

    @pytest.mark.parametrize("age_verified, order_hour, expected_valid", [
        (True, 12, True), (False, 12, False), (True, 1, False),
        (True, 23, True), (True, 8, True), (True, 7, False),
    ])
    def test_rule_4_alcohol(self, validator, age_verified, order_hour, expected_valid):
        order = create_base_order(has_alcohol=True, age_verified=age_verified, order_hour=order_hour)
        result = validator.validate_order(order)
        assert result["valid"] == expected_valid

    @pytest.mark.parametrize("total_amount, expected_risk", [
        (50000, 0.0), (100001, 0.9),
    ])
    def test_rule_5_risk_amount(self, validator, total_amount, expected_risk):
        order = create_base_order(total_amount=total_amount)
        result = validator.validate_order(order)
        assert result["risk_score"] == expected_risk


# ===== DECISION TABLE (ИСПРАВЛЕННАЯ) =====

@pytest.mark.parametrize("kwargs, expected_valid, expected_risk, expected_reasons", [
    # 1. Корректный заказ
    ({"total_amount": 500, "is_new": False}, True, 0.0, []),
    
    # 2. Сумма = 0 → НЕВАЛИД (текст ошибки из валидатора)
    ({"total_amount": 0, "is_new": False}, False, 0.0, ["Сумма заказа должна быть > 0 и < 1_000_000"]),
    
    # 3. Сумма > 1_000_000 → НЕВАЛИД + риск 0.9 (правило 5 срабатывает!)
    ({"total_amount": 1500000, "is_new": False}, False, 0.9, ["Сумма заказа должна быть > 0 и < 1_000_000"]),
    
    # 4. Новый пользователь, сумма > 15_000
    ({"total_amount": 20000, "is_new": True}, False, 0.0, ["Новый пользователь → сумма не более 15_000"]),
    
    # 5. Новый пользователь, сумма = 10_000
    ({"total_amount": 10000, "is_new": True}, True, 0.0, []),
    
    # 6. Кол-во позиций > 50
    ({"total_amount": 500, "total_items": 51}, False, 0.0, ["Количество позиций не должно превышать 50"]),
    
    # 7. Алкоголь, age_verified = False
    ({"total_amount": 500, "has_alcohol": True, "age_verified": False}, False, 0.0, ["Для алкоголя требуется age_verified = True"]),
    
    # 8. Алкоголь, время вне 08-23
    ({"total_amount": 500, "has_alcohol": True, "order_hour": 1}, False, 0.0, ["Алкоголь можно заказывать только с 08:00 до 23:00"]),
    
    # 9. Алкоголь, всё ок
    ({"total_amount": 500, "has_alcohol": True, "age_verified": True, "order_hour": 15}, True, 0.0, []),
    
    # 10. Сумма > 100_000 → риск 0.9
    ({"total_amount": 150000, "is_new": False}, True, 0.9, []),
    
    # 11. Смена email → +0.2
    ({"total_amount": 500, "email_changed_hours_ago": 0.5}, True, 0.2, []),
    
    # 12. Страна != кошелёк → +0.3
    ({"total_amount": 500, "delivery_country": "RU", "user_country": "KZ"}, True, 0.3, []),
])
def test_decision_table(validator, kwargs, expected_valid, expected_risk, expected_reasons):
    order = create_base_order(**kwargs)
    result = validator.validate_order(order)
    assert result["valid"] == expected_valid
    assert result["risk_score"] == expected_risk
    for reason in expected_reasons:
        assert reason in result["reasons"]

def test_invariant_valid_has_no_reasons(validator):
    order = create_base_order(total_amount=500, is_new=False)
    result = validator.validate_order(order)
    if result["valid"]:
        assert len(result["reasons"]) == 0


def test_invariant_risk_score_bounds(validator):
    for total_amount in [0, 1, 50000, 100000, 150000, 999999, 1000000]:
        order = create_base_order(total_amount=total_amount)
        result = validator.validate_order(order)
        assert 0.0 <= result["risk_score"] <= 1.0

def test_time_boundary_alcohol_invalid():
    validator = FakeValidator()
    order = create_base_order(has_alcohol=True, age_verified=True, order_hour=7)
    result = validator.validate_order(order)
    assert result["valid"] is False


def test_time_boundary_alcohol_valid():
    validator = FakeValidator()
    order = create_base_order(has_alcohol=True, age_verified=True, order_hour=8)
    result = validator.validate_order(order)
    assert result["valid"] is True


def test_duplicate_orders_stability():
    validator = FakeValidator()
    order = create_base_order()
    for i in range(10):
        result = validator.validate_order(order)
        assert "valid" in result
        assert "reasons" in result
        assert "risk_score" in result


def test_email_risk_boundary():
    validator = FakeValidator()
    order = create_base_order(email_changed_hours_ago=2)
    result = validator.validate_order(order)
    assert result["risk_score"] == 0.0

    order2 = create_base_order(email_changed_hours_ago=0.5)
    result2 = validator.validate_order(order2)
    assert result2["risk_score"] == 0.2

def test_chaos_mode_structure():
    validator = FakeValidator(chaos_mode=True)
    order = create_base_order()
    for _ in range(20):
        result = validator.validate_order(order)
        assert "valid" in result
        assert "reasons" in result
        assert "risk_score" in result
        assert isinstance(result["valid"], bool)
        assert isinstance(result["risk_score"], float)
        assert isinstance(result["reasons"], list)


def test_multiple_risks_combined():
    validator = FakeValidator()
    order = create_base_order(
        total_amount=150000,
        email_changed_hours_ago=0.5,
        delivery_country="RU",
        user_country="KZ"
    )
    result = validator.validate_order(order)
    assert result["risk_score"] == 1.0


def test_risk_does_not_exceed_one():
    validator = FakeValidator()
    order = create_base_order(
        total_amount=150000,
        email_changed_hours_ago=0.5,
        delivery_country="RU",
        user_country="KZ",
        has_alcohol=True,
        age_verified=True,
        order_hour=15
    )
    result = validator.validate_order(order)
    assert result["risk_score"] <= 1.0