# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added

- Initial release
- Synchronous client (`Pxshot`)
- Asynchronous client (`AsyncPxshot`)
- Screenshot capture with all options (format, quality, viewport, full page, wait conditions)
- Stored screenshots with URL response
- Usage statistics endpoint
- Health check endpoint
- Comprehensive exception hierarchy
- Rate limit header parsing
- Automatic retry with exponential backoff
- Pydantic models for type safety
- Full type hints
- pytest test suite
