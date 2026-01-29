"""Pydantic models for Pxshot API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ImageFormat(str, Enum):
    """Supported image formats."""

    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


class WaitUntil(str, Enum):
    """Page load wait conditions."""

    LOAD = "load"
    DOMCONTENTLOADED = "domcontentloaded"
    NETWORKIDLE = "networkidle"


class ScreenshotRequest(BaseModel):
    """Request model for screenshot capture."""

    url: str = Field(..., description="URL to capture")
    format: Optional[ImageFormat] = Field(None, description="Image format")
    quality: Optional[int] = Field(
        None, ge=1, le=100, description="Image quality (1-100, for JPEG/WEBP)"
    )
    width: Optional[int] = Field(None, ge=1, le=3840, description="Viewport width")
    height: Optional[int] = Field(None, ge=1, le=2160, description="Viewport height")
    full_page: Optional[bool] = Field(None, description="Capture full scrollable page")
    wait_until: Optional[WaitUntil] = Field(None, description="Wait condition")
    wait_for_selector: Optional[str] = Field(
        None, description="CSS selector to wait for"
    )
    wait_for_timeout: Optional[int] = Field(
        None, ge=0, le=30000, description="Additional wait time in ms"
    )
    device_scale_factor: Optional[float] = Field(
        None, ge=0.5, le=3, description="Device scale factor"
    )
    store: Optional[bool] = Field(
        None, description="Store screenshot and return URL instead of bytes"
    )

    model_config = ConfigDict(use_enum_values=True)


class StoredScreenshot(BaseModel):
    """Response model for stored screenshot."""

    url: str = Field(..., description="URL to access the stored screenshot")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    size_bytes: int = Field(..., description="Image size in bytes")


class UsageStats(BaseModel):
    """Response model for usage statistics."""

    period: str = Field(..., description="Billing period (e.g., '2024-01')")
    screenshots_used: int = Field(..., description="Screenshots taken this period")
    screenshots_limit: int = Field(..., description="Screenshot limit for the plan")
    storage_used_bytes: int = Field(..., description="Storage used in bytes")

    @property
    def screenshots_remaining(self) -> int:
        """Calculate remaining screenshots."""
        return max(0, self.screenshots_limit - self.screenshots_used)

    @property
    def usage_percentage(self) -> float:
        """Calculate usage percentage."""
        if self.screenshots_limit == 0:
            return 0.0
        return (self.screenshots_used / self.screenshots_limit) * 100


class HealthStatus(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Service status")
    version: Optional[str] = Field(None, description="API version")


class RateLimitInfo(BaseModel):
    """Rate limit information from response headers."""

    limit: Optional[int] = Field(None, description="Request limit")
    remaining: Optional[int] = Field(None, description="Remaining requests")
    reset: Optional[datetime] = Field(None, description="Rate limit reset time")

    @classmethod
    def from_headers(cls, headers: dict) -> "RateLimitInfo":
        """Parse rate limit info from HTTP headers."""
        limit = headers.get("x-ratelimit-limit")
        remaining = headers.get("x-ratelimit-remaining")
        reset = headers.get("x-ratelimit-reset")

        return cls(
            limit=int(limit) if limit else None,
            remaining=int(remaining) if remaining else None,
            reset=datetime.fromtimestamp(int(reset)) if reset else None,
        )


# Type alias for screenshot response
ScreenshotResponse = Union[bytes, StoredScreenshot]
