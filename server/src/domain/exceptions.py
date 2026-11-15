
class DatabaseError(Exception):
    def __init__(
        self,
        message: str,
    ) -> None:
        self.message = message
        super().__init__(message)

class PermissionDeniedError(Exception):
    def __init__(self, message: str = "Permission denied.") -> None:
        self.message = message
        super().__init__(message)
