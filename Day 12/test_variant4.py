"""
test_variant4.py - Тесты для варианта 4
"""

import pytest
from variant4_fixed import Account, PremiumAccount, process_accounts, LimitedCache


class TestAccount:
    def test_deposit(self):
        acc = Account("Alice", 1000)
        acc.deposit(500)
        assert acc.balance == 1500
        assert "Deposit: +500" in acc.get_history()
    
    def test_deposit_negative(self):
        acc = Account("Alice", 1000)
        with pytest.raises(ValueError, match="Amount must be positive"):
            acc.deposit(-100)
    
    def test_withdraw(self):
        acc = Account("Alice", 1000)
        acc.withdraw(300)
        assert acc.balance == 700
        assert "Withdraw: -300" in acc.get_history()
    
    def test_withdraw_insufficient(self):
        acc = Account("Alice", 100)
        with pytest.raises(ValueError, match="Insufficient funds"):
            acc.withdraw(200)
    
    def test_get_history(self):
        acc = Account("Alice", 1000)
        acc.deposit(500)
        acc.withdraw(200)
        history = acc.get_history()
        assert len(history) == 2
        assert history[0] == "Deposit: +500"
        assert history[1] == "Withdraw: -200"


class TestPremiumAccount:
    def test_premium_deposit(self):
        acc = PremiumAccount("Alice", 1000, 0.05)
        acc.deposit(500)
        assert acc.balance == 1500
        assert acc._bonus_points == 25.0
    
    def test_premium_inheritance(self):
        acc = PremiumAccount("Alice", 1000)
        assert hasattr(acc, '_bonus_points')
        acc.deposit(500)
        assert acc.balance == 1500


class TestProcessAccounts:
    def test_process_valid(self):
        data = [
            {'owner': 'Alice', 'balance': 1000, 'deposit': 500, 'withdraw': 200}
        ]
        results = process_accounts(data)
        assert len(results) == 1
        assert results[0]['owner'] == 'Alice'
        assert results[0]['balance'] == 1300
    
    def test_process_with_premium(self):
        data = [
            {'owner': 'Eve', 'balance': 100, 'deposit': 50, 'withdraw': 30, 'premium': True}
        ]
        results = process_accounts(data)
        assert results[0]['bonus_points'] == 2.5


class TestLimitedCache:
    def test_cache_size_limit(self):
        cache = LimitedCache(maxsize=3)
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3
        cache['d'] = 4
        assert len(cache) == 3
        assert 'a' not in cache
        assert 'b' in cache
        assert 'c' in cache
        assert 'd' in cache
