# errors.py

"""
Base class for HTTP errors
"""
class HTTPError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    """
    Convert error to a dictionary (useful for JSON responses)
    """
    def to_dict(self):
       return {'message': self.message, 'status_code': self.status_code}


class BadRequestError(HTTPError):
    def __init__(self, message: str):
        super().__init__(400, message)

class NotFoundError(HTTPError):
   def __init__(self, message: str):
        super().__init__(404, message)

class InternalServerError(HTTPError):
    def __init__(self, message: str):
        super().__init__(500, message)

class UnauthorizedError(HTTPError):
    def __init__(self, message: str):
        super().__init__(401, message)

class ForbiddenError(HTTPError):
    def __init__(self, message: str):
        super().__init__(403, message)

