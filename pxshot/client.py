"""Synchronous Pxshot client."""

from typing import Optional, Union

import httpx

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

DEFAULT_BASE_URL = "https://api.pxshot.com"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 3


class Pxshot:
    """Synchronous client for the Pxshot screenshot API.

    Example:
        >>> client = Pxshot('px_your_api_key')
        >>> image = client.screenshot(url='https://example.com')
        >>> with open('screenshot.png', 'wb') as f:
        ...     f.write(image)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        """Initialize the Pxshot client.

        Args:
            api_key: Your Pxshot API key (starts with 'px_')
            base_url: API base URL (default: https://api.pxshot.com)
            timeout: Request timeout in seconds (default: 60)
            max_retries: Maximum retry attempts for transient errors (default: 3)
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_rate_limit: Optional[RateLimitInfo] = None

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "pxshot-python/1.0.0",
            },
        )

    def __enter__(self) -> "Pxshot":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    @property
    def rate_limit(self) -> Optional[RateLimitInfo]:
        """Get rate limit info from the last request."""
        return self._last_rate_limit

    def _handle_response(
        self, response: httpx.Response, expect_json: bool = True
    ) -> Union[dict, bytes]:
        """Handle API response and raise appropriate exceptions."""
        self._last_rate_limit = RateLimitInfo.from_headers(dict(response.headers))

        if response.status_code == 200:
            if expect_json:
                return response.json()
            return response.content

        # Handle errors
        try:
            error_data = response.json()
            message = error_data.get("error", {}).get(
                "message", response.text
            ) or error_data.get("message", response.text)
        except Exception:
            error_data = None
            message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(message, error_data)
        elif response.status_code == 403:
            raise QuotaExceededError(message, error_data)
        elif response.status_code == 404:
            raise NotFoundError(message, error_data)
        elif response.status_code == 422:
            raise ValidationError(message, error_data)
        elif response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            raise RateLimitError(
                message,
                retry_after=int(retry_after) if retry_after else None,
                response=error_data,
            )
        elif response.status_code >= 500:
            raise ServerError(message, error_data)
        else:
            raise PxshotError(message, error_data)

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict] = None,
        expect_json: bool = True,
    ) -> Union[dict, bytes]:
        """Make an HTTP request with retry logic."""
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                response = self._client.request(method, path, json=json)
                return self._handle_response(response, expect_json=expect_json)
            except httpx.TimeoutException as e:
                last_error = TimeoutError(f"Request timed out: {e}")
            except httpx.ConnectError as e:
                last_error = ConnectionError(f"Failed to connect: {e}")
            except (RateLimitError, ServerError) as e:
                # Retry on rate limit and server errors
                last_error = e
                if attempt < self.max_retries - 1:
                    import time

                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    if isinstance(e, RateLimitError) and e.retry_after:
                        wait_time = min(e.retry_after, 60)
                    time.sleep(wait_time)
            except PxshotError:
                raise  # Don't retry client errors

        raise last_error  # type: ignore

    def screenshot(
        self,
        url: str,
        *,
        format: Optional[Union[ImageFormat, str]] = None,
        quality: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        full_page: Optional[bool] = None,
        wait_until: Optional[Union[WaitUntil, str]] = None,
        wait_for_selector: Optional[str] = None,
        wait_for_timeout: Optional[int] = None,
        device_scale_factor: Optional[float] = None,
        store: Optional[bool] = None,
    ) -> ScreenshotResponse:
        """Capture a screenshot of a URL.

        Args:
            url: The URL to capture
            format: Image format ('png', 'jpeg', 'webp')
            quality: Image quality 1-100 (for JPEG/WEBP)
            width: Viewport width in pixels
            height: Viewport height in pixels
            full_page: Capture the full scrollable page
            wait_until: Wait condition ('load', 'domcontentloaded', 'networkidle')
            wait_for_selector: CSS selector to wait for before capture
            wait_for_timeout: Additional wait time in milliseconds
            device_scale_factor: Device pixel ratio (0.5-3)
            store: If True, store the image and return a URL

        Returns:
            bytes: Raw image data if store=False (default)
            StoredScreenshot: Screenshot metadata with URL if store=True
        """
        request = ScreenshotRequest(
            url=url,
            format=ImageFormat(format) if format else None,
            quality=quality,
            width=width,
            height=height,
            full_page=full_page,
            wait_until=WaitUntil(wait_until) if wait_until else None,
            wait_for_selector=wait_for_selector,
            wait_for_timeout=wait_for_timeout,
            device_scale_factor=device_scale_factor,
            store=store,
        )

        payload = request.model_dump(exclude_none=True)

        # Convert snake_case to camelCase for API
        api_payload = {}
        for key, value in payload.items():
            # Convert snake_case to camelCase
            parts = key.split("_")
            camel_key = parts[0] + "".join(p.capitalize() for p in parts[1:])
            api_payload[camel_key] = value

        if store:
            data = self._request("POST", "/v1/screenshot", json=api_payload)
            return StoredScreenshot.model_validate(data)
        else:
            return self._request(
                "POST", "/v1/screenshot", json=api_payload, expect_json=False
            )  # type: ignore

    def usage(self) -> UsageStats:
        """Get current usage statistics.

        Returns:
            UsageStats: Usage information for the current billing period
        """
        data = self._request("GET", "/v1/usage")
        return UsageStats.model_validate(data)

    def health(self) -> HealthStatus:
        """Check API health status.

        Returns:
            HealthStatus: Service health information
        """
        data = self._request("GET", "/health")
        return HealthStatus.model_validate(data)
