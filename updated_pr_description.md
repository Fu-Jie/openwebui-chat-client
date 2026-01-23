# Release v0.1.15: Streaming chat fixes and optimizations

This PR prepares the release of v0.1.15, which focuses on streaming chat stability improvements and performance optimizations.

## Improvements and Optimizations

### Streaming Chat Fixes (修复流式chat)

- **Enhanced stability**: Improved error handling and connection management for streaming responses
- **Performance optimization**: Optimized streaming data processing and real-time response handling
- **Better timeout handling**: Enhanced timeout management for long-running streaming operations
- **Improved error recovery**: Better recovery mechanisms when streaming connections are interrupted

### Code Structure Improvements

- **Modular architecture benefits**: Refactored code structure improves maintainability and performance of chat operations
- **Better separation of concerns**: Chat and streaming logic are now better organized
- **Enhanced error handling**: Improved error propagation and logging across all chat functionalities

## Documentation Updates

Updated PyPI version badges in README files from 0.1.13 to 0.1.15 as requested in the GitHub development instructions, ensuring documentation accurately reflects the current release.

## Changes Made

- **Version bump**: Updated `pyproject.toml` from 0.1.14 to 0.1.15
- **Changelog management**: Moved unreleased changes to v0.1.15 section in both English and Chinese changelogs with release date 2025-01-28
- **README updates**: Updated PyPI badges from 0.1.13 to 0.1.15 in both `README.md` and `README.zh-CN.md`
- **Code cleanup**: Removed backup files and improved code structure for better maintainability
- **Release preparation**: Created git tag v0.1.15 with comprehensive release notes

## Release Process

All release files are prepared and ready. The GitHub Actions publish workflow will automatically build and deploy to PyPI when the tag is pushed.

## Testing

- All existing tests continue to pass
- Package imports successfully with new version
- Version number correctly updated across all relevant files
- Streaming chat functionality verified with improved stability
