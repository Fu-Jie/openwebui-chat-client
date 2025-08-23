# Changelog

All notable changes to this project will be documented in this file.

## [0.1.17] - 2025-08-23

### Added
- **Deep Research Agent**: Introduced the `deep_research` method, an autonomous agent that performs multi-step research on a topic using intelligent model routing between general and search-capable models.
- **HTTP Retry Mechanism**: Implemented a robust retry strategy in the base client for API calls, automatically retrying on transient server errors (5xx) to improve stability.

### Fixed
- **`create_model` Payload Fix**: Corrected the `create_model` method to send the full, accurate payload, including the `meta` object with capabilities, tags, etc., and fixed the endpoint URL to `/api/v1/models/create`.

## [0.1.16] - 2025-08-10

### Added
- **Prompts Management System**: Complete implementation of prompts functionality
  - `PromptsManager` module for managing custom prompts with variable substitution
  - Full CRUD operations: `get_prompts()`, `create_prompt()`, `update_prompt_by_command()`, `delete_prompt_by_command()`
  - Advanced variable extraction and substitution with `extract_variables()` and `substitute_variables()`
  - System variables support: `CURRENT_DATE`, `CURRENT_TIME`, `CURRENT_DATETIME`, `CURRENT_WEEKDAY`, `CURRENT_TIMEZONE`
  - Interactive prompt forms with typed variables (text, textarea, select, number, date, checkbox, etc.)
  - Search functionality: `search_prompts()` with filtering by command, title, or content
  - Batch operations: `batch_create_prompts()` and `batch_delete_prompts()` for efficient bulk management
  - Comprehensive examples in `examples/prompts_api/` with basic and advanced usage patterns
  - Full test coverage in `tests/test_prompts_functionality.py` 
  - Integration with CI test mapping for automated testing

## [0.1.15] - 2025-08-04

### Added
- **Continuous Conversation Feature**: New high-level conversation automation functionality
  - `continuous_chat()`: Automated multi-turn conversations with single models using follow-up suggestions
  - `continuous_parallel_chat()`: Automated multi-turn conversations across multiple models in parallel
  - `continuous_stream_chat()`: Automated multi-turn conversations with real-time streaming responses
  - Automatic follow-up question generation and random selection for natural conversation flow
  - Generic fallback questions when follow-ups are unavailable to ensure conversation continuity
  - Support for all existing chat parameters: model selection, folders, tags, RAG files/collections, tools, etc.
  - Comprehensive conversation history tracking and metadata collection
  - Full test coverage with focused unit tests in `tests/test_continuous_conversation.py`
  - Demonstration example in `examples/advanced_features/continuous_conversation.py`

## [0.1.14] - 2025-08-02

### Added in 0.1.14
- **Modular Architecture Refactor**: Complete restructuring of the codebase into modular components:
  - `openwebui_chat_client/core/base_client.py`: Core client functionality base class
  - `openwebui_chat_client/modules/chat_manager.py`: Dedicated chat management module
  - `openwebui_chat_client/modules/file_manager.py`: File operations management
  - `openwebui_chat_client/modules/knowledge_base_manager.py`: Knowledge base operations
  - `openwebui_chat_client/modules/model_manager.py`: Model management functionality
  - `openwebui_chat_client/modules/notes_manager.py`: Notes API management
- **Extended Example Suite**: New comprehensive examples and utilities:
  - `examples/advanced_features/archive_chats.py`: Chat archiving functionality demo
  - `examples/chat_features/model_switching.py`: Model switching examples
  - `examples/config/`: Configuration and environment setup examples  
  - `examples/utils/`: Shared utilities for example scripts
  - Enhanced documentation in `examples/README.md`
- **Comprehensive Test Suite**: Expanded test coverage with new test files:
  - `tests/test_archive_functionality.py`: Archive feature testing
  - `tests/test_changelog_extraction.py`: Changelog processing tests
  - `tests/test_documentation_structure.py`: Documentation validation tests
  - `tests/test_model_permissions.py`: Model permission testing
- **Archive Chat Functionality**: Added archive chat functionality with comprehensive tests and examples.
- **Batch Model Permissions Update**: Implemented batch model permissions update functionality.

### Changed in 0.1.14
- **Code Organization**: Migrated from monolithic structure to modular architecture while maintaining backward compatibility.
- **API Response Validation**: Fixed critical issues with API response validation and data format mismatches.
- **State Synchronization**: Resolved state synchronization issues between client and server.
- **Test Infrastructure**: Improved test reliability and integration test connectivity.
- **Documentation**: Comprehensive updates to all documentation files for better clarity and completeness.
- **Model Switching Example**: Updated `model_switching.py`.
- **List Chats Page Parameter**: Reverted `page` parameter to optional for `list_chats` method.

### Fixed in 0.1.14
- **Critical Test Failures**: Resolved multiple test failures related to modular refactor, API endpoints, response validation, chat object synchronization, and method delegation for mocking.
- **API Data Format Issues**: Fixed data format mismatches in API responses.
- **State Management**: Corrected state synchronization problems.
- **Model Configuration**: Fixed task model configuration issues.
- **Integration Connectivity**: Resolved integration test connectivity problems and critical test connectivity issues by preventing HTTP requests during client initialization.
- **Knowledge Base Delete Operations**: Completed fix for knowledge base delete operations with proper `ThreadPoolExecutor` delegation.
- **API Endpoint and Return Value Issues**: Fixed critical API endpoint and return value issues in notes and knowledge base operations.
- **Follow-up Test Failure**: Implemented proper task model fetching from config API to fix follow-up test failure.
- **Missing Critical Methods**: Implemented missing critical methods: `archive_chats_by_age`, `_get_chat_details`, `_cleanup_unused_placeholder_messages`.
- **Method Signatures and Return Types**: Fixed method signatures and return types for backward compatibility.
- **API Compatibility Issues**: Fixed API compatibility issues in refactored modular client.

## [0.1.13] - 2025-07-28

### Added in 0.1.13
- **Notes Management API**: Complete implementation of notes management functionality with full CRUD operations:
  - `get_notes()`: Retrieve all notes for the current user with detailed information
  - `get_notes_list()`: Get a simplified list of notes with only id, title, and timestamps
  - `create_note()`: Create new notes with title, data, metadata, and access control
  - `get_note_by_id()`: Retrieve specific notes by their ID
  - `update_note_by_id()`: Update existing notes with new content and metadata
  - `delete_note_by_id()`: Delete notes by their ID
- **Notes API Examples**: Added comprehensive example script `examples/notes_api/basic_notes.py` demonstrating all notes functionality
- **Notes Unit Tests**: Added complete test coverage in `tests/test_notes_functionality.py` with 118 test cases

### Changed in 0.1.13
- **Streamlined Release Process**: Simplified and optimized the release workflow documentation, removing redundant steps and improving clarity.
- **Enhanced Development Infrastructure**: Improved GitHub workflows, CI/CD setup, and development tooling for better maintainability.
- **Updated Project Organization**: Refined project structure and documentation organization for better developer experience.

## [0.1.12] - 2025-07-27

### Added in 0.1.12
- **Automatic Metadata Generation**: Added `enable_auto_tagging` and `enable_auto_titling` parameters to `chat`, `parallel_chat`, and `stream_chat` methods to automatically generate and apply tags and titles to conversations.
- **Manual Metadata Update**: Introduced a new public method `update_chat_metadata` that allows users to regenerate and update the tags and/or title for an existing chat by providing its `chat_id`.
- **Enhanced Return Values**: The `chat`, `parallel_chat`, and `stream_chat` methods now return `suggested_tags` and `suggested_title` in their response dictionaries when the corresponding features are enabled.
- **Unit Tests and Demos**: Added `tests/test_metadata_features.py` to test the new metadata functionalities and included a new demo in `examples/demos.py` to showcase their usage.

## [0.1.11] - 2025-07-26

### Added in 0.1.11
- **Streaming Chat Real-time Update Optimization**: Added real-time incremental content push functionality to the `stream_chat` method. By calling the `/api/v1/chats/{chat_id}/messages/{message_id}/event` interface, each content block is pushed to the Open WebUI frontend in real-time while streaming content is being generated, achieving a typewriter effect for real-time update experience.
- Added `_stream_delta_update` private method for real-time delta content updates during streaming chat.
- Added `examples/stream_chat_demo.py` demonstration script for the enhanced streaming functionality.
- **Chat Follow-up Generation Options**: Added support for follow-up generation options in chat methods.
- Automatically loads available model IDs during OpenWebUIClient initialization.
- Enhanced `get_model` method to automatically attempt model creation and retry fetching if the model does not exist and API returns 401.

### Changed in 0.1.11
- Added checks for empty `model_id` and local available model list in `get_model` method.
- Enhanced `_ask_stream` method to include real-time delta updates while maintaining backward compatibility.

## [0.1.10] - 2025-07-20

### Added in 0.1.10

- Added `stream_chat` method for single-model streaming chat functionality.
- Added `delete_all_knowledge_bases` method to delete all knowledge bases.
- Added `delete_knowledge_bases_by_keyword` method to delete knowledge bases by name keyword.
- Added `create_knowledge_bases_with_files` method to batch create knowledge bases and add files.

---

## [0.1.9] - 2025-07-13

### Added in 0.1.9

- Added `list_custom_models` method to list user-created custom models.
- Added `switch_chat_model` method to support switching models in existing chats.

### Changed in 0.1.9

- Refactored `list_models` and `list_base_models` methods for improved logging and robust response handling.

### Fixed in 0.1.9

- Corrected an issue where `list_models` and `list_base_models` might return incorrect data due to unexpected API response formats.

---

## [0.1.8] - 2025-07-08

### Changed in 0.1.8

- Standardized the return format for `chat` and `parallel_chat` to consistently provide detailed response objects, including `chat_id` and message identifiers.
- Improved logging and error handling for more robust API interactions.

### Fixed in 0.1.8

- Corrected the `tool_ids` parameter format to ensure proper tool usage in API requests.

---

## [0.1.7] - 2025-06-27

### Added in 0.1.7

- Improved and restructured README documentation.
- Added support for `tool_ids` and `image_paths` parameters in `chat`/`parallel_chat`.
- Enhanced API Reference and usage examples.

### Changed in 0.1.7

- Various documentation and usability improvements.

---

## [0.1.6] - 2025-06-25

### Added in 0.1.6

- Model management: list, create, update, delete custom models.
- Knowledge base management: create, add file, query.
- Chat organization: folders, tags, rename, move.
- RAG (Retrieval-Augmented Generation) support.
- Basic error handling and logging.

### Changed in 0.1.6

- Improved error messages and logging.
- Minor bug fixes.

---

## [0.1.5] - 2025-06-24

### Added in 0.1.5

- Support for chat folders and moving chats between folders.
- Tagging and renaming chats.

### Changed in 0.1.5

- Improved chat session caching.

---

## [0.1.4] - 2025-06-23

### Added in 0.1.4

- Parallel model chat (multi-model A/B test in one conversation).
- More robust session and file upload cache.

### Changed in 0.1.4

- Refactored chat and model APIs for extensibility.

---

## [0.1.3] - 2025-06-22

### Added in 0.1.3

- Knowledge base CRUD and file upload support.
- RAG integration in chat.

### Changed in 0.1.3

- Improved API error handling.

---

## [0.1.2] - 2025-06-21

### Added in 0.1.2

- Initial support for custom model creation and update.
- Basic logging and debug output.

### Changed in 0.1.2

- Minor improvements to chat API.

---

## [0.1.1] - 2025-06-20

### Added in 0.1.1

- Single-model chat and chat history.
- Basic project structure and packaging.

---

## [0.1.0] - 2025-06-20

### Added in 0.1.0

- Initial public release on PyPI.
- Core OpenWebUI chat client implementation.
