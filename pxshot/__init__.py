"""Pxshot - Official Python SDK for the Pxshot Screenshot API.

Example:
    >>> from pxshot import Pxshot
    >>> client = Pxshot('px_your_api_key')
    >>> image = client.screenshot(url='https://example.com')

    Async usage:
    >>> from pxshot import AsyncPxshot
    >>> async with AsyncPxshot('px_your_api_key') as client:
    ...     image = await client.screenshot(url='https://example.com')
"""

from .async_client import AsyncPxshot
from .client import Pxshot
from .exceptions import (
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    PxshotError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from .models import (
    HealthStatus,
    ImageFormat,
    RateLimitInfo,
    ScreenshotRequest,
    ScreenshotResponse,
    StoredScreenshot,
    UsageStats,
    WaitUntil,
)

__version__ = "1.0.0"
__all__ = [
    # Clients
    "Pxshot",
    "AsyncPxshot",
    # Models
    "ImageFormat",
    "WaitUntil",
    "ScreenshotRequest",
    "StoredScreenshot",
    "UsageStats",
    "HealthStatus",
    "RateLimitInfo",
    "ScreenshotResponse",
    # Exceptions
    "PxshotError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "QuotaExceededError",
    "ServerError",
    "TimeoutError",
    "ConnectionError",
]
