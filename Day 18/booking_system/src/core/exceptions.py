class DomainError(Exception):
    pass


class HotelNotFoundError(DomainError):
    pass


class RoomNotFoundError(DomainError):
    pass


class InvalidRatingError(DomainError):
    pass


class DuplicateRoomError(DomainError):
    pass


class HotelServiceError(DomainError):
    pass
