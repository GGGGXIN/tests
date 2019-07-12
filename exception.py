class APIError(Exception):
    def __init__(self, message):
        super().__init__(message)

    def to_dict(self):
        return dict(
            type=self.type,
            message=self.message,
            code=self.code,
            payload=self.payload)


class ValidationError(APIError):
    """客户端错误"""
    code = 2001
    message = "参数错误"
    type = "invalid_request"

