class ApiError(Exception):
    def __init__(self, message, status_code=None):
        super(ApiError, self).__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {'error': self.message}


class DoesNotExist(ApiError):
    status_code = 404


class ValidationError(ApiError):
    status_code = 400
