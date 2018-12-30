class ServerAvailabilityError(Exception):
    """Server is not available at the moment"""


class UnauthorizedException(Exception):
    """User is not authorized properly"""


class DialogNotFoundException(Exception):
    """Dialog with given UUID was not found"""


class LektaKernelError(Exception):
    """Lekta server exception"""
