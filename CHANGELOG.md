# Changelog

All notable changes to this project will be documented in this file.

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
