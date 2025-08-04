# Release v0.1.15: Add continuous conversation features, streaming chat fixes, and optimizations

This PR prepares the release of v0.1.15, which introduces comprehensive continuous conversation automation capabilities, includes streaming chat stability improvements, and implements continuous conversation optimizations.

## New Features in v0.1.15

### Continuous Conversation Automation
Added three new high-level conversation automation methods that enable automated multi-turn conversations:

- **`continuous_chat()`**: Automated multi-turn conversations with single models using follow-up suggestions
- **`continuous_parallel_chat()`**: Automated multi-turn conversations across multiple models in parallel  
- **`continuous_stream_chat()`**: Automated multi-turn conversations with real-time streaming responses

These methods feature:
- Automatic follow-up question generation and random selection for natural conversation flow
- Generic fallback questions when follow-ups are unavailable to ensure conversation continuity
- Support for all existing chat parameters: model selection, folders, tags, RAG files/collections, tools, etc.
- Comprehensive conversation history tracking and metadata collection
- Full test coverage with focused unit tests in `tests/test_continuous_conversation.py`
- Demonstration example in `examples/advanced_features/continuous_conversation.py`

## Improvements and Optimizations

### Streaming Chat Fixes (修复流式chat)
- **Enhanced stability**: Improved error handling and connection management for streaming responses
- **Performance optimization**: Optimized streaming data processing and real-time response handling
- **Better timeout handling**: Enhanced timeout management for long-running streaming operations
- **Improved error recovery**: Better recovery mechanisms when streaming connections are interrupted

### Continuous Conversation Optimizations (优化连续对话)
- **Intelligent follow-up generation**: Enhanced algorithm for generating more relevant and contextual follow-up questions
- **Conversation flow optimization**: Improved logic for maintaining natural conversation progression
- **Memory efficiency**: Optimized conversation history tracking and metadata management
- **Performance improvements**: Reduced latency in multi-turn conversation processing
- **Enhanced fallback mechanisms**: Better generic question selection when follow-ups are unavailable

### Code Structure Improvements
- **Modular architecture benefits**: Refactored code structure improves maintainability and performance of chat operations
- **Better separation of concerns**: Chat, streaming, and continuous conversation logic are now better organized
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
- Continuous conversation features tested with optimized performance