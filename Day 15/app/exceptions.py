class DeliveryCalculationError(Exception):
    """Ошибка при расчёте стоимости доставки"""
    pass


class DeliveryAPIError(Exception):
    """Ошибка при вызове внешнего API доставки"""
    pass
