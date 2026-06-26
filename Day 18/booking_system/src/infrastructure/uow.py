from contextlib import contextmanager
from typing import Type, Any


class UnitOfWork:
    def __init__(self):
        self._committed = False
        self._rolled_back = False

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        self._rolled_back = True

    @contextmanager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        elif not self._committed and not self._rolled_back:
            self.commit()
