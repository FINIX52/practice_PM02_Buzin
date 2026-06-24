import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import Base
from app.repositories import OrderRepository


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def repo(db_session: Session) -> OrderRepository:
    return OrderRepository(db_session)


@pytest.fixture
def sample_order_data():
    return {
        "customer_name": "Иван Петров",
        "delivery_address": "ул. Ленина, д. 10, кв. 5, Москва",
        "total_amount": 1500.0,
        "items": [
            {"product_name": "Товар 1", "quantity": 2, "price": 500.0},
            {"product_name": "Товар 2", "quantity": 1, "price": 500.0},
        ]
    }