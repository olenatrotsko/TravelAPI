class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(message)


class ConflictError(Exception):
    def __init__(self, message: str = "Conflict"):
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    def __init__(self, message: str = "Validation error"):
        self.message = message
        super().__init__(message)


class ExternalAPIError(Exception):
    def __init__(self, message: str = "External API error"):
        self.message = message
        super().__init__(message)


class UnauthorizedError(Exception):
    def __init__(self, message: str = "Unauthorized"):
        self.message = message
        super().__init__(message)
