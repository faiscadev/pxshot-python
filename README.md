# Pxshot Python SDK

Official Python SDK for the [Pxshot](https://pxshot.com) Screenshot API.

[![PyPI version](https://badge.fury.io/py/pxshot.svg)](https://badge.fury.io/py/pxshot)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- ✅ Sync and async clients
- ✅ Full type hints
- ✅ Pydantic models for request/response validation
- ✅ Automatic retry with exponential backoff
- ✅ Rate limit handling
- ✅ Comprehensive exception hierarchy

## Installation

```bash
pip install pxshot
```

## Quick Start

```python
from pxshot import Pxshot

# Initialize client
client = Pxshot('px_your_api_key')

# Capture a screenshot (returns bytes)
image = client.screenshot(url='https://example.com')

# Save to file
with open('screenshot.png', 'wb') as f:
    f.write(image)

# Don't forget to close when done (or use context manager)
client.close()
```

### Using Context Manager (Recommended)

```python
from pxshot import Pxshot

with Pxshot('px_your_api_key') as client:
    image = client.screenshot(url='https://example.com')
    with open('screenshot.png', 'wb') as f:
        f.write(image)
```

### Async Usage

```python
import asyncio
from pxshot import AsyncPxshot

async def main():
    async with AsyncPxshot('px_your_api_key') as client:
        # Capture screenshot
        image = await client.screenshot(url='https://example.com')
        
        # Save to file
        with open('screenshot.png', 'wb') as f:
            f.write(image)

asyncio.run(main())
```

## Screenshot Options

```python
from pxshot import Pxshot

with Pxshot('px_your_api_key') as client:
    image = client.screenshot(
        url='https://example.com',
        
        # Image format and quality
        format='jpeg',           # 'png', 'jpeg', 'webp'
        quality=80,              # 1-100 (for JPEG/WEBP)
        
        # Viewport settings
        width=1920,              # Viewport width
        height=1080,             # Viewport height
        device_scale_factor=2,   # Device pixel ratio (retina)
        
        # Page capture
        full_page=True,          # Capture full scrollable page
        
        # Wait conditions
        wait_until='networkidle',    # 'load', 'domcontentloaded', 'networkidle'
        wait_for_selector='.content', # Wait for element
        wait_for_timeout=5000,        # Additional wait (ms)
    )
```

## Storing Screenshots

Instead of receiving image bytes, you can store screenshots in Pxshot's cloud and get a URL:

```python
from pxshot import Pxshot

with Pxshot('px_your_api_key') as client:
    result = client.screenshot(
        url='https://example.com',
        store=True  # Store and return URL
    )
    
    print(f"URL: {result.url}")
    print(f"Expires: {result.expires_at}")
    print(f"Size: {result.width}x{result.height}")
    print(f"Bytes: {result.size_bytes}")
```

## Usage Statistics

```python
from pxshot import Pxshot

with Pxshot('px_your_api_key') as client:
    usage = client.usage()
    
    print(f"Period: {usage.period}")
    print(f"Used: {usage.screenshots_used}/{usage.screenshots_limit}")
    print(f"Remaining: {usage.screenshots_remaining}")
    print(f"Usage: {usage.usage_percentage:.1f}%")
    print(f"Storage: {usage.storage_used_bytes} bytes")
```

## Health Check

```python
from pxshot import Pxshot

with Pxshot('px_your_api_key') as client:
    health = client.health()
    print(f"Status: {health.status}")
```

## Rate Limiting

The SDK automatically tracks rate limit headers:

```python
from pxshot import Pxshot

with Pxshot('px_your_api_key') as client:
    image = client.screenshot(url='https://example.com')
    
    if client.rate_limit:
        print(f"Limit: {client.rate_limit.limit}")
        print(f"Remaining: {client.rate_limit.remaining}")
        print(f"Reset: {client.rate_limit.reset}")
```

## Error Handling

```python
from pxshot import (
    Pxshot,
    PxshotError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    ServerError,
    TimeoutError,
    ConnectionError,
)

with Pxshot('px_your_api_key') as client:
    try:
        image = client.screenshot(url='https://example.com')
    except AuthenticationError:
        print("Invalid API key")
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
    except ValidationError as e:
        print(f"Invalid request: {e.message}")
    except QuotaExceededError:
        print("Monthly quota exceeded")
    except ServerError:
        print("Server error, try again later")
    except TimeoutError:
        print("Request timed out")
    except ConnectionError:
        print("Failed to connect to API")
    except PxshotError as e:
        print(f"API error: {e.message}")
```

## Configuration

```python
from pxshot import Pxshot

client = Pxshot(
    'px_your_api_key',
    base_url='https://api.pxshot.com',  # Custom API URL
    timeout=60.0,                        # Request timeout (seconds)
    max_retries=3,                       # Retry attempts for transient errors
)
```

## Concurrent Screenshots (Async)

```python
import asyncio
from pxshot import AsyncPxshot

async def capture_many():
    urls = [
        'https://example.com',
        'https://github.com',
        'https://python.org',
    ]
    
    async with AsyncPxshot('px_your_api_key') as client:
        tasks = [client.screenshot(url=url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        for i, image in enumerate(results):
            with open(f'screenshot_{i}.png', 'wb') as f:
                f.write(image)

asyncio.run(capture_many())
```

## Models

### ScreenshotRequest

```python
from pxshot import ScreenshotRequest, ImageFormat, WaitUntil

request = ScreenshotRequest(
    url='https://example.com',
    format=ImageFormat.JPEG,
    quality=80,
    width=1920,
    height=1080,
    full_page=True,
    wait_until=WaitUntil.NETWORKIDLE,
    wait_for_selector='.content',
    wait_for_timeout=5000,
    device_scale_factor=2.0,
    store=True,
)
```

### StoredScreenshot

```python
from pxshot import StoredScreenshot

# Returned when store=True
result: StoredScreenshot
result.url          # str: URL to access screenshot
result.expires_at   # datetime: Expiration time
result.width        # int: Image width
result.height       # int: Image height
result.size_bytes   # int: File size
```

### UsageStats

```python
from pxshot import UsageStats

usage: UsageStats
usage.period                # str: Billing period (e.g., "2024-01")
usage.screenshots_used      # int: Screenshots taken
usage.screenshots_limit     # int: Plan limit
usage.storage_used_bytes    # int: Storage used
usage.screenshots_remaining # int: Remaining quota (computed)
usage.usage_percentage      # float: Usage % (computed)
```

## Development

```bash
# Clone repository
git clone https://github.com/pxshot/pxshot-python.git
cd pxshot-python

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy pxshot
```

## License

MIT License - see [LICENSE](LICENSE) for details.
