"""
variant_4.py - Классы с __slots__ (с ошибками)
Вариант 4
"""

import tracemalloc
import time
import sys

# Глобальный кеш для утечки памяти
CACHE = {}


class Account:
    """Класс аккаунта с __slots__"""
    __slots__ = ['_balance', 'owner', 'transactions']
    
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance
        self.transactions = []
        # ОШИБКА 1: Неправильное имя атрибута (typo)
        self.__history = []  # Должно быть self._history
    
    @property
    def balance(self):
        return self._balance
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._balance += amount
        # ОШИБКА 2: Обращение к несуществующему атрибуту
        self.transaction_history.append(f"Deposit: +{amount}")
        # Логическая ошибка: накопление в кеше
        CACHE[f"{self.owner}_{self._balance}"] = self._balance
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        self.transactions.append(f"Withdraw: -{amount}")
        # ОШИБКА 3: Логическая ошибка - двойной вычет
        self._balance = self._balance - amount * 0.95
    
    def get_history(self):
        # ОШИБКА 4: AttributeError из-за __slots__
        return self.transactions + self.__history
    
    def __getattr__(self, name):
        # ОШИБКА 5: Бесконечная рекурсия
        return getattr(self, name)


class PremiumAccount(Account):
    """Премиум аккаунт"""
    __slots__ = ['_cashback_rate']
    
    def __init__(self, owner, balance=0, cashback_rate=0.05):
        super().__init__(owner, balance)
        self._cashback_rate = cashback_rate
        # ОШИБКА 6: AttributeError (нет поля в __slots__)
        self._bonus_points = 0
    
    def deposit(self, amount):
        # ОШИБКА 7: Рекурсивный вызов без выхода
        return self.deposit(amount)


def process_accounts(accounts_data):
    """Обработка списка аккаунтов"""
    results = []
    for data in accounts_data:
        try:
            account = Account(data['owner'], data.get('balance', 0))
            account.deposit(data.get('deposit', 0))
            account.withdraw(data.get('withdraw', 0))
            results.append({
                'owner': account.owner,
                'balance': account.balance,
                'history': account.get_history()
            })
        except Exception as e:
            print(f"Error processing {data.get('owner', 'unknown')}: {e}")
            results.append({'owner': data.get('owner', 'unknown'), 'error': str(e)})
    return results


def create_test_data():
    """Создание тестовых данных"""
    return [
        {'owner': 'Alice', 'balance': 1000, 'deposit': 500, 'withdraw': 200},
        {'owner': 'Bob', 'balance': 500, 'deposit': 100, 'withdraw': 50},
        {'owner': 'Charlie', 'balance': 2000, 'deposit': 0, 'withdraw': 300},
        {'owner': 'Diana', 'balance': 300, 'deposit': 50, 'withdraw': 600},
        {'owner': 'Eve', 'balance': 100, 'deposit': 50, 'withdraw': 30},
    ]


def simulate_workload():
    """Имитация нагрузки для обнаружения утечек"""
    for i in range(100):
        data = {
            'owner': f'User_{i}',
            'balance': i * 100,
            'deposit': i % 10 * 10,
            'withdraw': i % 5 * 20
        }
        process_accounts([data])
        if i % 20 == 0:
            print(f"Processed {i+1} accounts, CACHE size: {len(CACHE)}")


if __name__ == "__main__":
    tracemalloc.start()
    
    print("=" * 60)
    print("Variant 4: Classes with __slots__")
    print("=" * 60)
    
    test_data = create_test_data()
    results = process_accounts(test_data)
    
    print("\nResults:")
    for r in results:
        print(r)
    
    print("\nSimulating workload...")
    simulate_workload()
    
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("\nTop 5 memory allocations:")
    for stat in top_stats[:5]:
        print(stat)
    
    print(f"\nFinal CACHE size: {len(CACHE)}")
