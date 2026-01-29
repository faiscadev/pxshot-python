"""Pxshot exception hierarchy."""

from typing import Any, Dict, Optional


class PxshotError(Exception):
    """Base exception for all Pxshot errors."""

    def __init__(self, message: str, response: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.response = response


class AuthenticationError(PxshotError):
    """Raised when API key is invalid or missing."""

    pass


class RateLimitError(PxshotError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, response)
        self.retry_after = retry_after


class ValidationError(PxshotError):
    """Raised when request parameters are invalid."""

    pass


class NotFoundError(PxshotError):
    """Raised when a resource is not found."""

    pass


class QuotaExceededError(PxshotError):
    """Raised when usage quota is exceeded."""

    pass


class ServerError(PxshotError):
    """Raised when the API returns a 5xx error."""

    pass


class TimeoutError(PxshotError):
    """Raised when a request times out."""

    pass


class ConnectionError(PxshotError):
    """Raised when unable to connect to the API."""

    pass
