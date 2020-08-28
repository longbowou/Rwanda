class JWTException(Exception):
    message = None

    def __init__(self):
        super().__init__(self.message)


class AccountRequiredException(JWTException):
    message = "ACCOUNT_REQUIRED"


class AnonymousAccountRequiredException(JWTException):
    message = "ANONYMOUS_ACCOUNT_REQUIRED"
