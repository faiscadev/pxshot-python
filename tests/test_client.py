"""Tests for the Pxshot SDK."""

import pytest
from pytest_httpx import HTTPXMock

from pxshot import (
    AsyncPxshot,
    AuthenticationError,
    Pxshot,
    QuotaExceededError,
    RateLimitError,
    StoredScreenshot,
    ValidationError,
)


class TestPxshotSync:
    """Tests for synchronous client."""

    def test_init_requires_api_key(self):
        """Test that API key is required."""
        with pytest.raises(ValueError, match="API key is required"):
            Pxshot("")

    def test_screenshot_returns_bytes(self, httpx_mock: HTTPXMock):
        """Test screenshot returns bytes when store=False."""
        image_data = b"\x89PNG\r\n\x1a\n..."
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            content=image_data,
        )

        with Pxshot("px_test_key") as client:
            result = client.screenshot(url="https://example.com")

        assert result == image_data

    def test_screenshot_returns_stored_screenshot(self, httpx_mock: HTTPXMock):
        """Test screenshot returns StoredScreenshot when store=True."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            json={
                "url": "https://storage.pxshot.com/abc123.png",
                "expires_at": "2024-12-31T23:59:59Z",
                "width": 1920,
                "height": 1080,
                "size_bytes": 123456,
            },
        )

        with Pxshot("px_test_key") as client:
            result = client.screenshot(url="https://example.com", store=True)

        assert isinstance(result, StoredScreenshot)
        assert result.url == "https://storage.pxshot.com/abc123.png"
        assert result.width == 1920
        assert result.height == 1080

    def test_screenshot_with_all_options(self, httpx_mock: HTTPXMock):
        """Test screenshot with all options."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            content=b"image",
        )

        with Pxshot("px_test_key") as client:
            client.screenshot(
                url="https://example.com",
                format="jpeg",
                quality=80,
                width=1920,
                height=1080,
                full_page=True,
                wait_until="networkidle",
                wait_for_selector=".content",
                wait_for_timeout=5000,
                device_scale_factor=2.0,
            )

        request = httpx_mock.get_request()
        assert request is not None
        body = request.read()
        assert b"url" in body
        assert b"format" in body
        assert b"quality" in body

    def test_usage_returns_stats(self, httpx_mock: HTTPXMock):
        """Test usage endpoint."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pxshot.com/v1/usage",
            json={
                "period": "2024-01",
                "screenshots_used": 100,
                "screenshots_limit": 1000,
                "storage_used_bytes": 5000000,
            },
        )

        with Pxshot("px_test_key") as client:
            usage = client.usage()

        assert usage.period == "2024-01"
        assert usage.screenshots_used == 100
        assert usage.screenshots_remaining == 900
        assert usage.usage_percentage == 10.0

    def test_health_check(self, httpx_mock: HTTPXMock):
        """Test health endpoint."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pxshot.com/health",
            json={"status": "ok", "version": "1.0.0"},
        )

        with Pxshot("px_test_key") as client:
            health = client.health()

        assert health.status == "ok"
        assert health.version == "1.0.0"

    def test_authentication_error(self, httpx_mock: HTTPXMock):
        """Test 401 raises AuthenticationError."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            status_code=401,
            json={"error": {"message": "Invalid API key"}},
        )

        with Pxshot("px_test_key") as client:
            with pytest.raises(AuthenticationError):
                client.screenshot(url="https://example.com")

    def test_validation_error(self, httpx_mock: HTTPXMock):
        """Test 422 raises ValidationError."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            status_code=422,
            json={"error": {"message": "Invalid URL"}},
        )

        with Pxshot("px_test_key") as client:
            with pytest.raises(ValidationError):
                client.screenshot(url="not-a-url")

    def test_rate_limit_error(self, httpx_mock: HTTPXMock):
        """Test 429 raises RateLimitError."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            status_code=429,
            headers={"retry-after": "60"},
            json={"error": {"message": "Rate limit exceeded"}},
        )

        with Pxshot("px_test_key", max_retries=1) as client:
            with pytest.raises(RateLimitError) as exc_info:
                client.screenshot(url="https://example.com")

        assert exc_info.value.retry_after == 60

    def test_quota_exceeded_error(self, httpx_mock: HTTPXMock):
        """Test 403 raises QuotaExceededError."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            status_code=403,
            json={"error": {"message": "Quota exceeded"}},
        )

        with Pxshot("px_test_key") as client:
            with pytest.raises(QuotaExceededError):
                client.screenshot(url="https://example.com")

    def test_rate_limit_headers_parsed(self, httpx_mock: HTTPXMock):
        """Test rate limit headers are parsed."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            content=b"image",
            headers={
                "x-ratelimit-limit": "100",
                "x-ratelimit-remaining": "99",
                "x-ratelimit-reset": "1704067200",
            },
        )

        with Pxshot("px_test_key") as client:
            client.screenshot(url="https://example.com")

        assert client.rate_limit is not None
        assert client.rate_limit.limit == 100
        assert client.rate_limit.remaining == 99


class TestPxshotAsync:
    """Tests for asynchronous client."""

    @pytest.mark.asyncio
    async def test_screenshot_returns_bytes(self, httpx_mock: HTTPXMock):
        """Test async screenshot returns bytes."""
        image_data = b"\x89PNG\r\n\x1a\n..."
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            content=image_data,
        )

        async with AsyncPxshot("px_test_key") as client:
            result = await client.screenshot(url="https://example.com")

        assert result == image_data

    @pytest.mark.asyncio
    async def test_screenshot_returns_stored_screenshot(self, httpx_mock: HTTPXMock):
        """Test async screenshot returns StoredScreenshot."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            json={
                "url": "https://storage.pxshot.com/abc123.png",
                "expires_at": "2024-12-31T23:59:59Z",
                "width": 1920,
                "height": 1080,
                "size_bytes": 123456,
            },
        )

        async with AsyncPxshot("px_test_key") as client:
            result = await client.screenshot(url="https://example.com", store=True)

        assert isinstance(result, StoredScreenshot)
        assert result.url == "https://storage.pxshot.com/abc123.png"

    @pytest.mark.asyncio
    async def test_usage_returns_stats(self, httpx_mock: HTTPXMock):
        """Test async usage endpoint."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pxshot.com/v1/usage",
            json={
                "period": "2024-01",
                "screenshots_used": 100,
                "screenshots_limit": 1000,
                "storage_used_bytes": 5000000,
            },
        )

        async with AsyncPxshot("px_test_key") as client:
            usage = await client.usage()

        assert usage.period == "2024-01"
        assert usage.screenshots_used == 100

    @pytest.mark.asyncio
    async def test_health_check(self, httpx_mock: HTTPXMock):
        """Test async health endpoint."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.pxshot.com/health",
            json={"status": "ok"},
        )

        async with AsyncPxshot("px_test_key") as client:
            health = await client.health()

        assert health.status == "ok"

    @pytest.mark.asyncio
    async def test_authentication_error(self, httpx_mock: HTTPXMock):
        """Test async 401 raises AuthenticationError."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.pxshot.com/v1/screenshot",
            status_code=401,
            json={"error": {"message": "Invalid API key"}},
        )

        async with AsyncPxshot("px_test_key") as client:
            with pytest.raises(AuthenticationError):
                await client.screenshot(url="https://example.com")
