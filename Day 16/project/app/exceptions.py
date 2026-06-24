class EntityNotFoundException(Exception):
    """Исключение: сущность не найдена в БД"""
    pass


class DeliveryCalculationException(Exception):
    """Исключение: ошибка при вызове API доставки"""
    pass
