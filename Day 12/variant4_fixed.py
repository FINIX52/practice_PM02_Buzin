"""
variant_4_fixed.py - Исправленная версия (Вариант 4)
"""

import tracemalloc
from collections import OrderedDict


# Исправление 1: LRU-кеш вместо бесконечного
class LimitedCache:
    """Кеш с ограничением размера"""
    def __init__(self, maxsize=100):
        self._cache = OrderedDict()
        self.maxsize = maxsize
    
    def __setitem__(self, key, value):
        self._cache[key] = value
        self._cache.move_to_end(key)
        if len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)
    
    def __getitem__(self, key):
        return self._cache[key]
    
    def __len__(self):
        return len(self._cache)
    
    def clear(self):
        self._cache.clear()


CACHE = LimitedCache(maxsize=100)


class Account:
    """Класс аккаунта с __slots__ (исправлен)"""
    # Исправление: добавлен _history в __slots__
    __slots__ = ['_balance', 'owner', 'transactions', '_history']
    
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance
        self.transactions = []
        # Исправление: правильное имя
        self._history = []
    
    @property
    def balance(self):
        return self._balance
    
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._balance += amount
        # Исправление: правильный атрибут
        self.transactions.append(f"Deposit: +{amount}")
        self._history.append(f"Deposit: +{amount}")
        CACHE[f"{self.owner}_{self._balance}"] = self._balance
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        # Исправление: только один вычет
        self._balance -= amount
        self.transactions.append(f"Withdraw: -{amount}")
        self._history.append(f"Withdraw: -{amount}")
    
    def get_history(self):
        # Исправление: правильный атрибут
        return self.transactions + self._history
    
    def __getattr__(self, name):
        # Исправление: защита от бесконечной рекурсии
        if name in self.__slots__:
            return getattr(self, name)
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")


class PremiumAccount(Account):
    """Премиум аккаунт"""
    # Исправление: добавлен _bonus_points в __slots__
    __slots__ = ['_cashback_rate', '_bonus_points']
    
    def __init__(self, owner, balance=0, cashback_rate=0.05):
        super().__init__(owner, balance)
        self._cashback_rate = cashback_rate
        self._bonus_points = 0
    
    def deposit(self, amount):
        # Исправление: вызов родительского метода
        super().deposit(amount)
        self._bonus_points += amount * self._cashback_rate


def process_accounts(accounts_data):
    """Обработка списка аккаунтов"""
    results = []
    for data in accounts_data:
        try:
            if data.get('premium', False):
                account = PremiumAccount(
                    data['owner'],
                    data.get('balance', 0),
                    data.get('cashback_rate', 0.05)
                )
            else:
                account = Account(data['owner'], data.get('balance', 0))
            
            account.deposit(data.get('deposit', 0))
            account.withdraw(data.get('withdraw', 0))
            results.append({
                'owner': account.owner,
                'balance': account.balance,
                'history': account.get_history(),
                'bonus_points': getattr(account, '_bonus_points', 0)
            })
        except Exception as e:
            results.append({
                'owner': data.get('owner', 'unknown'),
                'error': str(e)
            })
    return results


def create_test_data():
    """Создание тестовых данных"""
    return [
        {'owner': 'Alice', 'balance': 1000, 'deposit': 500, 'withdraw': 200},
        {'owner': 'Bob', 'balance': 500, 'deposit': 100, 'withdraw': 50},
        {'owner': 'Charlie', 'balance': 2000, 'deposit': 0, 'withdraw': 300},
        {'owner': 'Diana', 'balance': 300, 'deposit': 50, 'withdraw': 600},
        {'owner': 'Eve', 'balance': 100, 'deposit': 50, 'withdraw': 30, 'premium': True},
    ]


def simulate_workload():
    """Имитация нагрузки"""
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
    print("Variant 4: Classes with __slots__ (FIXED)")
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
