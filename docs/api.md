# API Reference

This document provides a detailed reference for all classes and methods in the `openwebui-chat-client` library.

---

## OpenWebUIClient (Synchronous)

The main facade for interacting with Open WebUI services synchronously.

### Chat Operations

#### `chat(question, chat_id=None, model=None, chat_title=None, **kwargs)`
Send a message to an AI model and receive a response.
- **Returns**: `ChatResponse` object.
- **Key Attributes**: `.content` (the text), `.chat_id`, `.message_id`.

#### `parallel_chat(question, model_ids, **kwargs)`
Query multiple models simultaneously.
- **Returns**: `ParallelChatResponse` object.
- **Key Attributes**: `.responses` (dict of ChatResponse), `.chat_id`.

#### `stream_chat(question, **kwargs)`
Send a message and receive a generator for real-time streaming.
- **Yields**: `str` (text chunks).

### Action Management & Execution

#### `get_actions()`
Retrieve a list of all triggerable functions of type `action`.
- **Returns**: `List[Function]`.

#### `trigger_action(action_id, chat_id, message_id, params=None)`
Executes a server-side action and automatically synchronizes the UI state.

The SDK includes a **Smart Synchronization Engine** that handles the following formats:

| Format | Detection | SDK Sync Strategy | UI Result |
| :--- | :--- | :--- | :--- |
| **Artifacts Mode** | Raw HTML string response | Wraps HTML in Markdown block and appends to message `content`. | Triggers the **Artifacts panel** on the right side of the UI. |
| **Embeds Mode** | JSON containing `embeds` | Injects the data into the message's `embeds` list. | Displays **RichUI components** (buttons, cards, etc.) inside the chat. |
| **Legacy Mode** | JSON containing `messages` | Surgically merges updated message objects into the chat history. | Updates text or metadata of existing messages. |

---

## Models (Pydantic V2)

All data returned by the client is encapsulated in Pydantic V2 models for type safety and validation.

### `ChatResponse`
- `content`: str (The assistant's reply)
- `text`: str (Alias for content)
- `chat_id`: str
- `message_id`: str
- `sources`: List[dict] (Optional)
- `embeds`: List[dict] (Optional)

### `Function`
- `id`: str
- `name`: str
- `type`: str ('action', 'filter', or 'pipe')
- `is_action`: bool (Helper property)

---

## Managers

Advanced users can access sub-managers directly via `client._manager_name`.

- `_functions_manager`: For plugin and action management.
- `_model_manager`: For listing and checking model availability.
- `_file_manager`: For direct file uploads and encoding.
- `_knowledge_base_manager`: For RAG collection operations.
