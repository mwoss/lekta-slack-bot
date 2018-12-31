class LektaAPIError(Exception):
    """General API exception"""


class ServerAvailabilityError(LektaAPIError):
    """Server is not available at the moment"""


class UnauthorizedException(LektaAPIError):
    def __init__(self, error_code: int):
        self.error_code = error_code
        super().__init__("User was not authorized properly")


class DialogNotFoundException(LektaAPIError):
    def __init__(self, error_code: int):
        self.error_code = error_code
        super().__init__("Dialog with given UUID was not found")


class LektaKernelError(LektaAPIError):
    def __init__(self, error_code: int):
        self.error_code = error_code
        super().__init__("Lekta general backend error")
