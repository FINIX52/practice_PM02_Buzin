import pytest
from src.hotel import create_test_data


@pytest.fixture
def service():
    """Фикстура с тестовыми данными"""
    return create_test_data()
