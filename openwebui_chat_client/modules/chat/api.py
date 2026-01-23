"""Chat API Layer - Direct HTTP Interface to Open WebUI Backend.

This module provides a clean, type-safe interface to all Open WebUI chat-related
API endpoints. Each method corresponds to an official FastAPI endpoint in the
backend/open_webui/routers/ directory.

Architecture:
    - Pure API layer: No business logic, only HTTP requests
    - Type-safe: All methods use TypedDict types from .types module
    - Error handling: Comprehensive exception handling with detailed logging
    - Retry logic: Automatic retries for transient connection errors

Official Backend Reference:
    - backend/open_webui/routers/chats.py (main chat endpoints)
    - backend/open_webui/routers/folders.py (folder management)
    - backend/open_webui/routers/files.py (file uploads)
    - backend/open_webui/main.py (completion endpoints)

Method Naming Convention:
    - CRUD operations: create_*, get_*, update_*, delete_*
    - List operations: list_*, get_all_*
    - State changes: pin_*, archive_*, clone_*, share_*
    - Search/Query: search_*, get_*_by_*

Usage Example:
    ```python
    from openwebui_chat_client.core.base_client import BaseClient
    from openwebui_chat_client.modules.chat.api import ChatAPI

    base_client = BaseClient(base_url, auth_token)
    chat_api = ChatAPI(base_client)

    # Create new chat
    payload = {"chat": {"title": "Test", "history": {...}}}
    chat = chat_api.create_chat(payload)

    # Get completion
    completion_payload = {
        "model": "gpt-4.1",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False
    }
    response = chat_api.completion(completion_payload)
    ```

Error Handling:
    All methods return None or empty lists on failure, with detailed error logs.
    Use logging level INFO to see operation status, DEBUG for payloads.

See Also:
    - ChatPayloads: For building request payloads
    - ChatWorkflow: For orchestrating multi-step operations
    - types.py: For type definitions
"""

from typing import Any, Dict, List, Optional, Generator
import os
import logging
import time
import requests.exceptions
from openwebui_chat_client.core.base_client import BaseClient

# Type definitions
from .types import (
    ChatDict,
    ChatFormDict,
    CompletionPayloadDict,
    CompletedPayloadDict,
    ResponseDict,
    FileDict,
    TagDict,
    FolderDict,
    ChatID,
    MessageID,
    FileID,
    FolderID,
)

logger = logging.getLogger(__name__)


class ChatAPI:
    """
    Chat API Layer - Strictly follows Open WebUI Backend API.

    Based on: backend/open_webui/routers/chats.py
    Each method corresponds to an actual FastAPI endpoint.
    """

    def __init__(self, base_client: BaseClient):
        self.base_client = base_client

    # =================================================================
    # Core Chat Completion Flow
    # =================================================================

    def completion(self, payload: CompletionPayloadDict) -> Optional[ResponseDict]:
        """Generate chat completion response (OpenAI-compatible endpoint).

        This is the primary endpoint for chat interactions. It processes the user's
        message through the specified model and returns a completion response.
        Supports both streaming and non-streaming modes, tools, RAG, and multimodal inputs.

        Official Backend: backend/open_webui/main.py:1565-1857 @app.post("/api/chat/completions")

        Args:
            payload: Completion request payload containing:
                - model (str): Model ID (e.g., "gpt-4.1", "gemini-2.5-flash")
                - messages (List[Dict]): OpenAI-format message array
                - stream (bool): Enable streaming response
                - chat_id (Optional[str]): Chat ID for persistence
                - metadata (Optional[Dict]): Tracking metadata (message_id, session_id)
                - tool_ids (Optional[List[str]]): Enabled tool IDs
                - files (Optional[List[Dict]]): File attachments for multimodal
                - temperature, top_p, max_tokens, etc.: Model parameters

        Returns:
            OpenAI-format completion response with:
            {
                "id": str,  # Completion ID
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": str,  # Generated response
                        "tool_calls": [...] if tools used
                    },
                    "finish_reason": "stop" | "tool_calls" | "length"
                }],
                "usage": {"prompt_tokens": int, "completion_tokens": int}
            }
            Returns None if request fails after retries.

        Raises:
            No exceptions raised; failures return None with error logging.

        Example:
            ```python
            # Simple chat completion
            payload = {
                "model": "gpt-4.1",
                "messages": [
                    {"role": "user", "content": "What is Python?"}
                ],
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 500
            }

            response = chat_api.completion(payload)
            if response:
                answer = response["choices"][0]["message"]["content"]
                print(answer)

            # With tools enabled
            payload_with_tools = {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Search for latest AI news"}],
                "tool_ids": ["web_search", "calculator"],
                "stream": False
            }
            response = chat_api.completion(payload_with_tools)
            ```

        Notes:
            - Automatic retry for connection errors (max 3 attempts)
            - Timeout handling for long-running requests
            - Logs all errors with traceback for debugging
            - For streaming responses, use stream_completion() instead

        Official Backend Flow:
            1. Validate payload (model, messages, metadata)
            2. Process through inlet filters (if configured)
            3. Apply RAG if files/knowledge base specified
            4. Execute tool calls if tools enabled
            5. Call model provider (OpenAI/Ollama/etc.)
            6. Process response through outlet filters
            7. Return formatted response
        """
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                return self.base_client._get_json_response(
                    "POST", "/api/chat/completions", json_data=payload
                )
            except requests.exceptions.ConnectionError as e:
                logger.warning(
                    f"Completion request connection error (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(
                        f"Completion request failed after {max_retries} attempts: {e}"
                    )
                    return None
            except requests.exceptions.Timeout as e:
                logger.error(f"Completion request timeout: {e}")
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Completion request failed: {e}", exc_info=True)
                return None
            except Exception as e:
                logger.error(f"Unexpected error in completion: {e}", exc_info=True)
                return None

    def stream_completion(
        self, payload: CompletionPayloadDict
    ) -> Optional[Generator[bytes, None, None]]:
        """Generate streaming chat completion (real-time token-by-token response).

        Streaming variant of completion() that returns Server-Sent Events (SSE) stream.
        Provides real-time updates as the model generates tokens, enabling responsive UX.

        Official Backend: backend/open_webui/main.py:1565-1857 @app.post("/api/chat/completions")

        Args:
            payload: Same as completion(), but stream=True is required:
                - model (str): Model ID
                - messages (List[Dict]): Message history
                - stream (bool): Must be True
                - session_id (str): Required for Socket.IO event routing
                - Other parameters same as completion()

        Returns:
            Generator yielding SSE data chunks (bytes):
            - Each chunk: b'data: {json_object}\n\n'
            - Events:
                * {"choices": [{"delta": {"content": "token"}}]} - New tokens
                * {"choices": [{"finish_reason": "stop"}]} - Stream end
                * {"error": {...}} - Error occurred
            Returns None if stream initialization fails.

        Yields:
            bytes: SSE formatted data chunks

        Example:
            ```python
            import json

            # Start streaming completion
            payload = {
                "model": "gpt-4.1",
                "messages": [{"role": "user", "content": "Write a poem"}],
                "stream": True,
                "session_id": "unique-session-id"
            }

            stream = chat_api.stream_completion(payload)
            if stream:
                full_response = ""
                for chunk in stream:
                    # Parse SSE chunk
                    if chunk.startswith(b'data: '):
                        data_str = chunk[6:].decode('utf-8').strip()
                        if data_str == '[DONE]':
                            break

                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                full_response += content
                                print(content, end="", flush=True)
                        except json.JSONDecodeError:
                            continue

                print(f"\n\nComplete response: {full_response}")
            ```

        Notes:
            - Requires WebSocket/SSE-capable client for full real-time experience
            - Backend emits Socket.IO events (chat:completion, chat:completion:delta)
            - Stream may be interrupted on connection loss
            - Always consume entire stream or close connection properly
            - For non-streaming, use completion() for simpler handling

        Official Backend Streaming Flow:
            1. Validate stream=True and session_id presence
            2. Set up SSE response headers
            3. Process through inlet filters
            4. Call model provider with stream=True
            5. For each token:
               - Emit Socket.IO event (if session active)
               - Yield SSE formatted chunk
               - Buffer for tool call detection
            6. Process tool calls if detected
            7. Apply outlet filters on complete response
            8. Emit final event with usage stats

        See Also:
            - completion(): For non-streaming completion
            - completed(): For finalizing streamed conversations
        """
        try:
            return self.base_client._stream_request(
                "POST", "/api/chat/completions", json_data=payload
            )
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Stream completion connection error: {e}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"Stream completion timeout: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Stream completion request failed: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in stream completion: {e}", exc_info=True)
            return None

    def completed(self, payload: CompletedPayloadDict) -> Optional[Dict[str, Any]]:
        """Finalize chat completion and trigger background tasks.

        Called after completion to apply outlet filters and execute background tasks
        such as title generation, tags extraction, follow-up suggestions, and image generation.
        This is an automatic step in the official Open WebUI frontend workflow.

        Official Backend: backend/open_webui/main.py:1859-1900 @app.post("/api/chat/completed")

        Args:
            payload: Completion finalization data:
                - chat_id (str): Chat identifier
                - message_id (str): Message identifier (assistant message)
                - model (Optional[str]): Model used for generation
                - messages (Optional[List[Dict]]): Full message history
                - session_id (Optional[str]): Session identifier
                - Additional task configuration flags

        Returns:
            Background task results:
            {
                "title": str,  # Generated title (if first turn)
                "tags": List[str],  # Extracted tags
                "follow_ups": List[str],  # Follow-up suggestions
                "status": "success"
            }
            Returns None if request fails.

        Example:
            ```python
            # After getting completion response
            completion_resp = chat_api.completion(payload)

            # Finalize and get background task results
            completed_payload = {
                "chat_id": "chat-123",
                "message_id": "msg-456",
                "model": "gpt-4.1",
                "messages": messages,  # Full history
                "session_id": "session-789"
            }

            results = chat_api.completed(completed_payload)
            if results:
                print(f"Title: {results.get('title')}")
                print(f"Tags: {results.get('tags')}")
                print(f"Follow-ups: {results.get('follow_ups')}")
            ```

        Background Tasks Triggered:
            1. Title Generation: Auto-generate chat title (first 2 messages only)
            2. Tags Generation: Extract relevant tags for categorization
            3. Follow-up Generation: Suggest next questions
            4. Image Generation: Generate images if detected in request

        Notes:
            - Non-critical: Failure doesn't affect completion result
            - Tasks run asynchronously in backend
            - Results may not be immediately available
            - Only title generation runs for first turn

        Official Backend Reference:
            - backend/open_webui/main.py:1859-1900 (completed endpoint)
            - backend/open_webui/utils/middleware.py:1909-2157 (background_tasks_handler)
        """
        try:
            return self.base_client._get_json_response(
                "POST", "/api/chat/completed", json_data=payload
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Completed request failed: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in completed: {e}", exc_info=True)
            return None

    # =================================================================
    # Chat CRUD Operations
    # =================================================================

    def create_chat(self, payload: ChatFormDict) -> Optional[ChatDict]:
        """Create a new chat session with full message history.

        Creates a new chat in the Open WebUI database with complete message tree structure.
        This is the primary method for programmatically creating chat sessions.

        Official Backend: backend/open_webui/routers/chats.py:82-135 @router.post("/new")

        Args:
            payload: Chat creation payload:
                - chat (ChatBodyDict): Inner chat object containing:
                    * title (str): Chat title
                    * history (ChatHistoryDict): Message tree with:
                        - currentId (str): Active message ID
                        - messages (Dict[str, MessageDict]): Message dictionary
                    * models (List[str]): Model IDs used
                    * params (Dict): Model parameters
                - folder_id (Optional[str]): Folder assignment

        Returns:
            Complete chat object:
            {
                "id": str,  # Generated chat ID
                "user_id": str,  # Owner user ID
                "title": str,
                "chat": {  # Inner chat object
                    "title": str,
                    "history": {...},
                    "models": [...],
                    "params": {...}
                },
                "folder_id": str | None,
                "meta": {"tags": [], "pinned": False},
                "created_at": int,  # Unix timestamp
                "updated_at": int
            }
            Returns None if creation fails.

        Example:
            ```python
            from openwebui_chat_client.modules.chat.payloads import ChatPayloads

            # Build message tree
            user_msg = ChatPayloads.build_user_message(
                content="Hello, how are you?",
                model="gpt-4.1"
            )
            assistant_msg = ChatPayloads.build_assistant_message(
                content="I'm doing well, thank you!",
                model="gpt-4.1",
                parent_id=user_msg["id"]
            )

            # Build complete payload
            payload = ChatPayloads.build_chat_payload(
                title="Friendly Conversation",
                messages=[user_msg, assistant_msg],
                current_id=assistant_msg["id"],
                folder_id="folder-123",
                models=["gpt-4.1"]
            )

            # Create chat
            chat = chat_api.create_chat(payload)
            if chat:
                print(f"Created chat: {chat['id']}")
                print(f"Title: {chat['title']}")
            ```

        Validation:
            - payload must have "chat" field
            - chat.history must have valid structure
            - currentId must exist in messages dictionary
            - User must have permission to create chats

        Notes:
            - Chat ID is auto-generated by backend
            - Tags can be added separately via add_chat_tag()
            - Folder must exist before assignment
            - Created chat is immediately visible in UI

        Official Backend Flow:
            1. Validate user permissions
            2. Generate chat ID
            3. Validate chat structure
            4. Create ChatModel instance
            5. Save to database
            6. Return complete chat object

        See Also:
            - ChatPayloads.build_chat_payload(): Helper for building payloads
            - update_chat(): For updating existing chats
            - get_chat(): For retrieving chats
        """
        try:
            if not payload or "chat" not in payload:
                logger.error("Invalid create_chat payload: missing 'chat' field")
                return None

            return self.base_client._get_json_response(
                "POST", "/api/v1/chats/new", json_data=payload
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Create chat request failed: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in create_chat: {e}", exc_info=True)
            return None

    def get_chat(self, chat_id: ChatID) -> Optional[ChatDict]:
        """Retrieve a single chat with full message history.

        Fetches complete chat object including all messages, metadata, and folder assignment.
        This is the primary method for accessing chat data programmatically.

        Official Backend: backend/open_webui/routers/chats.py:138-149 @router.get("/{id}")

        Args:
            chat_id: Chat identifier (UUID string)

        Returns:
            Complete chat object (same structure as create_chat return value):
            {
                "id": str,
                "user_id": str,
                "title": str,
                "chat": {
                    "title": str,
                    "history": {
                        "currentId": str,
                        "messages": {msg_id: message_object, ...}
                    },
                    "models": [str, ...],
                    "params": {...}
                },
                "folder_id": str | None,
                "meta": {"tags": [...], "pinned": bool},
                "created_at": int,
                "updated_at": int,
                "archived": bool,
                "share_id": str | None
            }
            Returns None if chat not found or access denied.

        Example:
            ```python
            # Get specific chat
            chat = chat_api.get_chat("chat-uuid-123")
            if chat:
                print(f"Title: {chat['title']}")
                print(f"Messages: {len(chat['chat']['history']['messages'])}")

                # Access message tree
                messages = chat['chat']['history']['messages']
                current_id = chat['chat']['history']['currentId']
                current_msg = messages[current_id]
                print(f"Latest: {current_msg['content']}")
            else:
                print("Chat not found or access denied")
            ```

        Notes:
            - Requires chat ownership or admin permissions
            - Returns full message tree (not just current branch)
            - Includes all metadata (tags, pinned, archived status)
            - Efficient for single chat retrieval

        See Also:
            - list_chats(): For listing multiple chats
            - search_chats(): For finding chats by query
            - get_all_chats(): For bulk retrieval
        """
        try:
            if not chat_id or not isinstance(chat_id, str):
                logger.error(f"Invalid chat_id: {chat_id}")
                return None

            return self.base_client._get_json_response(
                "GET", f"/api/v1/chats/{chat_id}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Get chat request failed for chat_id={chat_id}: {e}", exc_info=True
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error in get_chat for chat_id={chat_id}: {e}",
                exc_info=True,
            )
            return None

    def update_chat(self, chat_id: ChatID, payload: ChatFormDict) -> Optional[ChatDict]:
        """Update an existing chat (full or partial update).

        Updates chat data including message history, title, folder assignment.
        The backend merges the provided data with existing chat object.

        Official Backend: backend/open_webui/routers/chats.py:152-200 @router.post("/{id}")

        Args:
            chat_id: Chat identifier to update
            payload: Update payload:
                - chat (ChatBodyDict): Updated chat data (merged with existing)
                    * Can include partial updates (only changed fields)
                    * To add messages: include updated history.messages
                    * To change title: include updated title
                - folder_id (Optional[str]): Move to different folder

        Returns:
            Updated chat object (same structure as get_chat return value)
            Returns None if update fails.

        Example:
            ```python
            # Example 1: Add new message to existing chat
            chat = chat_api.get_chat("chat-123")
            messages = list(chat['chat']['history']['messages'].values())

            # Build new assistant message
            new_msg = ChatPayloads.build_assistant_message(
                content="Here's the answer...",
                model="gpt-4.1",
                parent_id=messages[-1]["id"]
            )
            messages.append(new_msg)

            # Update chat
            update_payload = ChatPayloads.build_chat_payload(
                title=chat['title'],
                messages=messages,
                current_id=new_msg["id"],
                models=chat['chat']['models']
            )
            updated = chat_api.update_chat("chat-123", update_payload)

            # Example 2: Change title only
            update_payload = {
                "chat": {
                    "title": "New Title",
                    # Other fields will be preserved from existing chat
                }
            }
            chat_api.update_chat("chat-123", update_payload)

            # Example 3: Move to folder
            update_payload = {
                "chat": chat['chat'],  # Keep existing chat data
                "folder_id": "folder-456"  # Change folder
            }
            chat_api.update_chat("chat-123", update_payload)
            ```

        Update Behavior:
            - Merge strategy: Provided fields override, missing fields preserved
            - history.messages: Replaces entire message dictionary
            - models: Replaces entire list
            - params: Merges with existing parameters
            - folder_id: Null removes from folder

        Validation:
            - Must be chat owner or have admin permissions
            - Chat must exist
            - Message structure must be valid
            - currentId must exist in messages

        Notes:
            - Use for appending messages after completion
            - Updated_at timestamp automatically updated
            - Triggers re-indexing for search
            - Cannot update user_id or id fields

        Official Backend Flow:
            1. Fetch existing chat
            2. Validate ownership
            3. Merge provided data with existing
            4. Validate merged structure
            5. Save to database
            6. Update search index
            7. Return updated chat

        See Also:
            - create_chat(): For creating new chats
            - get_chat(): For retrieving current state
            - ChatPayloads.build_chat_payload(): Helper for building payloads
        """
        try:
            if not chat_id or not isinstance(chat_id, str):
                logger.error(f"Invalid chat_id: {chat_id}")
                return None
            if not payload or "chat" not in payload:
                logger.error(
                    f"Invalid update_chat payload for chat_id={chat_id}: missing 'chat' field"
                )
                return None

            return self.base_client._get_json_response(
                "POST", f"/api/v1/chats/{chat_id}", json_data=payload
            )
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Update chat request failed for chat_id={chat_id}: {e}", exc_info=True
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error in update_chat for chat_id={chat_id}: {e}",
                exc_info=True,
            )
            return None

    def delete_chat(self, chat_id: ChatID) -> bool:
        """Delete a single chat permanently.

        Permanently removes a chat and performs cleanup:
        - Deletes chat record from database
        - Removes orphaned tags (tags used only by this chat)
        - Cannot be undone (consider archive_chat for soft delete)

        Official Backend Reference:
            - routers/chats.py:203-227 @router.delete("/{id}")

        Args:
            chat_id (str): Chat identifier (UUID string)

        Returns:
            bool: True if deletion successful, False otherwise

        Example:
            ```python
            # Delete a chat
            success = chat_api.delete_chat("chat-uuid-123")
            if success:
                print("Chat deleted successfully")
            else:
                print("Failed to delete chat")

            # Verify deletion
            chat = chat_api.get_chat("chat-uuid-123")
            assert chat is None  # Chat no longer exists
            ```

        Notes:
            - Requires chat ownership or admin permissions
            - Tags cleanup: If tag used only by this chat, tag is deleted
            - Shared chats: Deletion removes share link
            - Archived chats: Can still be deleted
            - No undo: Consider archive_chat() for reversible hiding

        See Also:
            - delete_all_chats(): Bulk delete all user chats
            - archive_chat(): Soft delete (reversible)
        """
        try:
            if not chat_id or not isinstance(chat_id, str):
                logger.error(f"Invalid chat_id: {chat_id}")
                return False

            resp = self.base_client._make_request("DELETE", f"/api/v1/chats/{chat_id}")
            success = resp is not None and resp.status_code == 200

            if not success:
                logger.warning(
                    f"Delete chat failed for chat_id={chat_id}, status_code={resp.status_code if resp else 'None'}"
                )

            return success
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Delete chat request failed for chat_id={chat_id}: {e}", exc_info=True
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error in delete_chat for chat_id={chat_id}: {e}",
                exc_info=True,
            )
            return False

    # =================================================================
    # Chat List & Query Operations
    # =================================================================

    def list_chats(
        self,
        page: Optional[int] = None,
        include_pinned: bool = False,
        include_folders: bool = False,
    ) -> List[ChatDict]:
        """List user's chats with pagination and optional metadata.

        Primary method for retrieving chat lists in paginated format.
        Returns lightweight chat objects (title, id, updated_at) without full message history.
        Ideal for UI chat lists and search results.

        Official Backend Reference:
            - routers/chats.py:230-266 @router.get("/")
            - routers/chats.py:269-304 @router.get("/list")

        Args:
            page (Optional[int]): Page number (1-indexed), 60 chats per page.
                                 None returns all chats (default)
            include_pinned (bool): Include pinned status in meta field
            include_folders (bool): Include folder_id and folder hierarchy

        Returns:
            List[ChatDict]: List of chat objects:
            [
                {
                    "id": str,
                    "user_id": str,
                    "title": str,
                    "updated_at": int,  # Unix timestamp
                    "created_at": int,
                    "archived": bool,
                    "meta": {"pinned": bool} if include_pinned,
                    "folder_id": str | None if include_folders
                },
                ...
            ]
            Returns empty list if no chats or on error.

        Example:
            ```python
            # Get first page of chats
            chats = chat_api.list_chats(page=1)
            for chat in chats:
                print(f"{chat['title']}: {chat['updated_at']}")

            # Get all chats with metadata
            all_chats = chat_api.list_chats(
                include_pinned=True,
                include_folders=True
            )

            pinned = [c for c in all_chats if c.get('meta', {}).get('pinned')]
            print(f"Pinned chats: {len(pinned)}")
            ```

        Pagination:
            - Page size: 60 chats (backend configured)
            - Ordering: Most recently updated first (DESC)
            - Empty page: Returns empty list (not error)

        Performance:
            - Fast: No message history loaded
            - Efficient: Indexed database queries
            - Cached: Backend may cache recent results

        Notes:
            - Excludes archived chats (use get_archived_chats instead)
            - Does not include full chat history (use get_chat for complete data)
            - Page=None may be slow for users with 1000+ chats

        See Also:
            - get_all_chats(): Get full chat objects with history
            - search_chats(): Search chats by text
            - get_archived_chats(): List archived chats
        """
        try:
            params = {}
            if page is not None:
                if not isinstance(page, int) or page < 1:
                    logger.warning(f"Invalid page number: {page}, using default")
                else:
                    params["page"] = page
            if include_pinned:
                params["include_pinned"] = True
            if include_folders:
                params["include_folders"] = True

            resp = self.base_client._get_json_response(
                "GET", "/api/v1/chats/", params=params
            )

            if not isinstance(resp, list):
                logger.warning(f"List chats returned non-list response: {type(resp)}")
                return []

            return resp
        except requests.exceptions.RequestException as e:
            logger.error(f"List chats request failed: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error in list_chats: {e}", exc_info=True)
            return []

    def get_all_chats(self) -> List[ChatDict]:
        """Retrieve all user chats with complete data (not paginated).

        Returns full chat objects including message history, metadata, and folders.
        This is a heavyweight operation - use list_chats() for UI lists.
        Intended for bulk operations, exports, and analytics.

        Official Backend Reference:
            - routers/chats.py:307-326 @router.get("/all")

        Returns:
            List[ChatDict]: Complete chat objects:
            [
                {
                    "id": str,
                    "user_id": str,
                    "title": str,
                    "chat": {  # Full chat object
                        "title": str,
                        "history": {
                            "currentId": str,
                            "messages": {msg_id: message_object}
                        },
                        "models": [str],
                        "params": {...}
                    },
                    "folder_id": str | None,
                    "meta": {"tags": [...], "pinned": bool},
                    "created_at": int,
                    "updated_at": int,
                    "archived": bool,
                    "share_id": str | None
                },
                ...
            ]
            Returns empty list if no chats or on error.

        Example:
            ```python
            # Export all chats
            all_chats = chat_api.get_all_chats()
            print(f"Total chats: {len(all_chats)}")

            # Calculate total messages
            total_messages = sum(
                len(chat['chat']['history']['messages'])
                for chat in all_chats
            )
            print(f"Total messages: {total_messages}")

            # Find chats using specific model
            gpt4_chats = [
                chat for chat in all_chats
                if 'gpt-4' in chat['chat'].get('models', [])
            ]
            ```

        Performance:
            - Slow: Loads full message trees for all chats
            - Memory: Can be large (MB-scale for users with many chats)
            - Not cached: Fresh database query each time

        Use Cases:
            - Data export and backup
            - Analytics and statistics
            - Bulk chat processing
            - Migration to other systems

        Warnings:
            - For 100+ chats: May take several seconds
            - For 1000+ chats: Consider pagination or streaming
            - Large response: May exceed memory limits in constrained environments

        Notes:
            - Excludes archived chats by default
            - Includes all message branches (not just active path)
            - Does not include deleted chats

        See Also:
            - list_chats(): Lightweight paginated list
            - get_archived_chats(): For archived chats
            - search_chats(): For filtered retrieval
        """
        resp = self.base_client._get_json_response("GET", "/api/v1/chats/all")
        return resp if isinstance(resp, list) else []

    def search_chats(
        self, query: str, page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search chats by text query with special tag filtering support.

        Performs full-text search across chat titles and message content.
        Supports special "tag:" prefix for filtering by tags.
        Returns paginated results ordered by relevance.

        Official Backend Reference:
            - routers/chats.py:390-415 @router.get("/search")

        Args:
            query (str): Search query string
                        - Normal text: searches titles and content
                        - "tag:tagname": filters chats with specific tag
                        - Example: "tag:work" finds all work-tagged chats
            page (Optional[int]): Page number (1-indexed), 60 results per page
                                 None returns all matches (default)

        Returns:
            List[Dict]: Matching chat objects (lightweight, no full history):
            [
                {
                    "id": str,
                    "title": str,
                    "updated_at": int,
                    "created_at": int,
                    "meta": {"tags": [...]},
                    # Relevance score may be included
                },
                ...
            ]
            Returns empty list if no matches or on error.

        Example:
            ```python
            # Text search
            results = chat_api.search_chats("Python tutorial")
            for chat in results:
                print(f"Found: {chat['title']}")

            # Tag filtering
            work_chats = chat_api.search_chats("tag:work")
            print(f"Work chats: {len(work_chats)}")

            # Combined with pagination
            first_page = chat_api.search_chats(
                query="machine learning",
                page=1
            )

            # Find chats mentioning specific model
            gpt4_chats = chat_api.search_chats("gpt-4")
            ```

        Search Behavior:
            - Case-insensitive matching
            - Searches chat title and message content
            - Partial word matching supported
            - Results ordered by relevance (most recent + keyword density)

        Tag Search:
            - Prefix "tag:" triggers tag filtering
            - Case-sensitive tag matching
            - Exact tag name required
            - Returns chats with that tag

        Performance:
            - Indexed search: Fast for large chat collections
            - First page typically < 100ms
            - Full search (page=None) may be slow for 1000+ chats

        Notes:
            - Excludes archived chats from results
            - Empty query returns empty list (not all chats)
            - Special characters in query are escaped

        See Also:
            - get_chats_by_tag(): Direct tag filtering
            - list_chats(): For unfiltered listings
        """
        params = {"text": query}
        if page is not None:
            params["page"] = page
        resp = self.base_client._get_json_response(
            "GET", "/api/v1/chats/search", params=params
        )
        return resp if isinstance(resp, list) else []

    def get_archived_chats(
        self,
        page: Optional[int] = None,
        query: Optional[str] = None,
        order_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List archived chats with advanced filtering and sorting.

        Retrieves chats that have been archived (soft-deleted).
        Archived chats are hidden from normal chat lists but not permanently deleted.
        Supports search, pagination, and custom ordering.

        Official Backend Reference:
            - routers/chats.py:329-387 @router.get("/archived")

        Args:
            page (Optional[int]): Page number (1-indexed), 60 chats per page
                                 None returns all archived chats
            query (Optional[str]): Search query for filtering by title/content
            order_by (Optional[str]): Sort field ("created_at" | "updated_at" | "title")
                                     Defaults to "updated_at"
            direction (Optional[str]): Sort direction ("asc" | "desc")
                                      Defaults to "desc"

        Returns:
            List[Dict]: Archived chat objects (same structure as list_chats)
            Returns empty list if no archived chats or on error.

        Example:
            ```python
            # Get all archived chats
            archived = chat_api.get_archived_chats()
            print(f"Archived chats: {len(archived)}")

            # Search archived chats
            results = chat_api.get_archived_chats(
                query="project",
                order_by="updated_at",
                direction="desc"
            )

            # Paginated retrieval
            first_page = chat_api.get_archived_chats(page=1)
            second_page = chat_api.get_archived_chats(page=2)

            # Restore all archived chats
            for chat in archived:
                chat_api.archive_chat(chat['id'])  # Toggle archives
            ```

        Archive Behavior:
            - Archived chats hidden from normal lists
            - Tags removed when archived (if unique to chat)
            - Can be restored via archive_chat() toggle
            - Can be permanently deleted

        Notes:
            - Archived ≠ Deleted: Can be restored
            - Search: Full-text search across title and messages
            - Empty result: Returns [] not None

        See Also:
            - archive_chat(): Toggle archive status
            - archive_all_chats(): Bulk archive
            - unarchive_all_chats(): Bulk restore
        """
        params = {}
        if page is not None:
            params["page"] = page
        if query:
            params["query"] = query
        if order_by:
            params["order_by"] = order_by
        if direction:
            params["direction"] = direction

        resp = self.base_client._get_json_response(
            "GET", "/api/v1/chats/archived", params=params
        )
        return resp if isinstance(resp, list) else []

    def get_pinned_chats(self) -> List[Dict[str, Any]]:
        """Retrieve all pinned chats for the current user.

        Returns chats marked as pinned (favorite/starred) for quick access.
        Pinned chats typically appear at the top of chat lists in UI.
        Lightweight query - does not include full message history.

        Official Backend Reference:
            - routers/chats.py:418-431 @router.get("/pinned")

        Returns:
            List[Dict]: Pinned chat objects (lightweight):
            [
                {
                    "id": str,
                    "title": str,
                    "updated_at": int,
                    "created_at": int,
                    "meta": {"pinned": True},
                    "folder_id": str | None,
                    ...
                },
                ...
            ]
            Returns empty list if no pinned chats or on error.

        Example:
            ```python
            # Get pinned chats
            pinned = chat_api.get_pinned_chats()
            print(f"Pinned chats: {len(pinned)}")

            for chat in pinned:
                print(f"- {chat['title']}")

            # Check if specific chat is pinned
            chat_id = "chat-123"
            is_pinned = any(c['id'] == chat_id for c in pinned)
            print(f"Chat {chat_id} pinned: {is_pinned}")

            # Get full data for pinned chats
            for chat in pinned:
                full_chat = chat_api.get_chat(chat['id'])
                # Process full message history...
            ```

        Notes:
            - Fast: Indexed query, no message loading
            - Ordered by pin date (most recent first)
            - Excludes archived chats

        See Also:
            - pin_chat(): Toggle pin status
            - get_pinned_status(): Check single chat pin status
        """
        resp = self.base_client._get_json_response("GET", "/api/v1/chats/pinned")
        return resp if isinstance(resp, list) else []

    def delete_all_chats(self) -> bool:
        """Permanently delete all user chats (DESTRUCTIVE).

        Deletes every chat (active and archived) owned by the current user.
        This is a permanent, irreversible operation. All chat history is lost.
        Use with extreme caution.

        Official Backend Reference:
            - routers/chats.py:625-637 @router.delete("/")

        Returns:
            bool: True if bulk deletion successful, False on error

        Example:
            ```python
            # WARNING: This example is destructive!
            # Always confirm before executing

            # Check chat count first
            chats = chat_api.list_chats()
            archived = chat_api.get_archived_chats()
            total = len(chats) + len(archived)
            print(f"About to delete {total} chats")

            # Confirm with user
            confirm = input("Type 'DELETE ALL' to confirm: ")
            if confirm == "DELETE ALL":
                success = chat_api.delete_all_chats()
                if success:
                    print("All chats deleted permanently")

            # Verify deletion
            remaining = chat_api.list_chats()
            assert len(remaining) == 0
            ```

        Operation Details:
            - Affects: ALL user chats (active + archived)
            - Permanent: Cannot be undone
            - Fast: Optimized bulk delete
            - Cleanup: Removes all tags, shares, folder assignments

        Deleted Data:
            - All message history
            - All tags (user-specific)
            - All share links
            - All folder assignments
            - All metadata

        Warnings:
            - ⚠️ IRREVERSIBLE: No recovery possible
            - ⚠️ No confirmation dialog in API
            - ⚠️ Affects all chats, no exceptions
            - Consider export backup before deletion

        Use Cases:
            - Account closure
            - Complete data wipe
            - Testing cleanup
            - Starting completely fresh

        Notes:
            - Requires user permissions (cannot delete others' chats)
            - Shared chats: Links become invalid
            - Tags: Removed if no other users reference them

        See Also:
            - delete_chat(): Delete single chat
            - archive_all_chats(): Reversible alternative
            - get_all_chats(): Export before deletion
        """
        resp = self.base_client._make_request("DELETE", "/api/v1/chats/")
        return resp is not None and resp.status_code == 200

    # =================================================================
    # Chat State Management (Pin, Archive, Clone, Share)
    # =================================================================

    def pin_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Toggle pin status of a chat (favorite/star).

        Marks or unmarks a chat as pinned for quick access.
        Pinned chats appear at top of chat lists and in dedicated pinned section.
        This is a toggle operation - calling again will unpin.

        Official Backend Reference:
            - routers/chats.py:520-541 @router.post("/{id}/pin")

        Args:
            chat_id (str): Chat identifier to pin/unpin

        Returns:
            Optional[Dict]: Updated chat object with new pin status:
            {
                "id": str,
                "title": str,
                "meta": {
                    "pinned": bool,  # New pin status
                    "tags": [...]
                },
                "updated_at": int,
                ...
            }
            Returns None if operation fails.

        Example:
            ```python
            # Pin a chat (favorite)
            result = chat_api.pin_chat("chat-123")
            if result:
                is_pinned = result['meta'].get('pinned', False)
                print(f"Chat pinned: {is_pinned}")

            # Unpin by calling again
            result = chat_api.pin_chat("chat-123")
            print(f"Chat unpinned: {not result['meta']['pinned']}")

            # Pin multiple important chats
            important_chats = ["chat-1", "chat-2", "chat-3"]
            for chat_id in important_chats:
                chat_api.pin_chat(chat_id)

            # List all pinned chats
            pinned = chat_api.get_pinned_chats()
            print(f"Pinned count: {len(pinned)}")
            ```

        Pin Behavior:
            - Toggle: pinned ↔ unpinned
            - UI: Pinned chats at top of list
            - Persists across sessions
            - Survives archiving (can pin archived chats)

        Use Cases:
            - Mark frequently accessed chats
            - Bookmark important conversations
            - Quick access to active projects

        Notes:
            - No limit on pinned chats
            - Pin status independent of tags
            - Archived chats can be pinned
            - Deleted chats: Pin status lost

        See Also:
            - get_pinned_chats(): List all pinned chats
            - get_pinned_status(): Check current pin status
        """
        return self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}/pin"
        )

    def get_pinned_status(self, chat_id: str) -> Optional[bool]:
        """Check if a chat is currently pinned.

        Retrieves the pin status of a single chat without loading full chat data.
        Lightweight query for checking pin state.

        Official Backend Reference:
            - routers/chats.py:544-560 @router.get("/{id}/pinned")

        Args:
            chat_id (str): Chat identifier to check

        Returns:
            Optional[bool]: Pin status
                - True: Chat is pinned
                - False: Chat is not pinned
                - None: Chat not found or error

        Example:
            ```python
            # Check pin status
            is_pinned = chat_api.get_pinned_status("chat-123")
            if is_pinned is None:
                print("Chat not found")
            elif is_pinned:
                print("Chat is pinned")
            else:
                print("Chat is not pinned")

            # Conditional pin
            if not chat_api.get_pinned_status("chat-456"):
                chat_api.pin_chat("chat-456")
                print("Pinned chat")
            ```

        Notes:
            - Fast: No message loading
            - Returns None for non-existent chats
            - Does not modify chat state

        See Also:
            - pin_chat(): Toggle pin status
            - get_pinned_chats(): List all pinned chats
        """
        return self.base_client._get_json_response(
            "GET", f"/api/v1/chats/{chat_id}/pinned"
        )

    def archive_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Toggle archive status of a chat (soft delete).

        Archives or unarchives a chat by toggling its archived flag.
        Archived chats are hidden from normal lists but not deleted.
        This is the reversible alternative to delete_chat().

        Official Backend Reference:
            - routers/chats.py:563-592 @router.post("/{id}/archive")

        Args:
            chat_id (str): Chat identifier (UUID string)

        Returns:
            Optional[Dict]: Updated chat object with new archived status:
            {
                "id": str,
                "title": str,
                "archived": bool,  # New status
                "updated_at": int,
                ...
            }
            Returns None if operation fails.

        Example:
            ```python
            # Archive a chat (hide it)
            result = chat_api.archive_chat("chat-123")
            if result:
                print(f"Archived: {result['archived']}")

            # Unarchive (restore)
            result = chat_api.archive_chat("chat-123")  # Toggle again
            print(f"Restored: {not result['archived']}")

            # Check archive status
            chat = chat_api.get_chat("chat-123")
            if chat and chat.get('archived'):
                print("Chat is archived")
            ```

        Archive Behavior:
            - Toggle operation: archived ↔ not archived
            - Archived chats hidden from list_chats()
            - Still accessible via get_chat() and get_archived_chats()
            - Can be permanently deleted while archived

        Tag Cleanup:
            - When archiving: Removes tags unique to this chat
            - Shared tags (used by other chats) are preserved
            - When unarchiving: Tags NOT automatically restored

        Use Cases:
            - Clean up UI without losing chat history
            - Temporarily hide old conversations
            - Organize chats by lifecycle stage

        Notes:
            - Reversible: Can toggle back to unarchive
            - Does not affect share status
            - Folder assignment preserved
            - Timestamps updated on toggle

        See Also:
            - delete_chat(): Permanent deletion
            - archive_all_chats(): Bulk archive
            - get_archived_chats(): List archived chats
        """
        return self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}/archive"
        )

    def archive_all_chats(self) -> bool:
        """Archive all user chats in bulk (mass soft delete).

        Archives every non-archived chat owned by the current user.
        This is a bulk version of archive_chat() for each chat.
        Useful for account cleanup or starting fresh.

        Official Backend Reference:
            - routers/chats.py:595-607 @router.post("/archive/all")

        Returns:
            bool: True if bulk archive successful, False on error

        Example:
            ```python
            # Archive all chats
            success = chat_api.archive_all_chats()
            if success:
                print("All chats archived")

            # Verify
            active = chat_api.list_chats()
            archived = chat_api.get_archived_chats()
            print(f"Active: {len(active)}, Archived: {len(archived)}")

            # Restore all
            if chat_api.unarchive_all_chats():
                print("All chats restored")
            ```

        Operation Details:
            - Affects: All non-archived chats
            - Atomic: Either all succeed or all fail (transaction)
            - Fast: Optimized bulk update query

        Effects:
            - All chats hidden from list_chats()
            - Tags cleaned up (shared tags preserved)
            - Share links remain active
            - Folder assignments preserved

        Use Cases:
            - Clean slate: Hide all past conversations
            - Account cleanup before handoff
            - Testing: Reset chat state

        Notes:
            - Reversible via unarchive_all_chats()
            - Does not delete chats (use delete_all_chats for that)
            - Already archived chats unaffected

        See Also:
            - unarchive_all_chats(): Restore all chats
            - delete_all_chats(): Permanent bulk deletion
            - archive_chat(): Single chat archive
        """
        resp = self.base_client._make_request("POST", "/api/v1/chats/archive/all")
        return resp is not None and resp.status_code == 200

    def unarchive_all_chats(self) -> bool:
        """Restore all archived chats to active status (bulk unarchive).

        Unarchives every archived chat owned by the current user.
        This reverses the effects of archive_all_chats().
        Restores chats to normal visibility in chat lists.

        Official Backend Reference:
            - routers/chats.py:610-622 @router.post("/unarchive/all")

        Returns:
            bool: True if bulk unarchive successful, False on error

        Example:
            ```python
            # Restore all archived chats
            success = chat_api.unarchive_all_chats()
            if success:
                print("All chats restored")

            # Verify restoration
            active = chat_api.list_chats()
            archived = chat_api.get_archived_chats()
            print(f"Active: {len(active)}, Archived: {len(archived)}")
            assert len(archived) == 0
            ```

        Operation Details:
            - Affects: All archived chats
            - Atomic: Either all succeed or all fail
            - Fast: Optimized bulk update

        Effects:
            - All archived chats visible in list_chats() again
            - Timestamps updated (updated_at)
            - Tags NOT automatically restored (must add manually)

        Use Cases:
            - Undo archive_all_chats()
            - Restore account after cleanup
            - Recover from accidental bulk archive

        Notes:
            - Already active chats unaffected
            - Does not restore deleted tags
            - Share links remain valid

        See Also:
            - archive_all_chats(): Bulk archive
            - archive_chat(): Single chat toggle
        """
        resp = self.base_client._make_request("POST", "/api/v1/chats/unarchive/all")
        return resp is not None and resp.status_code == 200

    def clone_chat(
        self, chat_id: str, title: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a complete copy of an existing chat.

        Clones a chat with all its message history, creating an independent copy.
        Useful for branching conversations, experimentation, or sharing templates.
        The cloned chat references the original via originalChatId metadata.

        Official Backend Reference:
            - routers/chats.py:625-665 @router.post("/{id}/clone")

        Args:
            chat_id (str): Source chat identifier to clone
            title (Optional[str]): Custom title for cloned chat
                                  Defaults to "Clone of {original_title}"

        Returns:
            Optional[Dict]: Newly created chat object:
            {
                "id": str,  # New chat ID (different from source)
                "title": str,  # Custom or auto-generated title
                "chat": {  # Complete copy of message history
                    "history": {...},
                    "models": [...],
                    "originalChatId": str  # Reference to source
                },
                "created_at": int,  # New timestamp
                "updated_at": int,
                ...
            }
            Returns None if cloning fails.

        Example:
            ```python
            # Clone with default title
            cloned = chat_api.clone_chat("chat-123")
            if cloned:
                print(f"Cloned: {cloned['id']}")
                print(f"Title: {cloned['title']}")  # "Clone of Original Title"

            # Clone with custom title
            experiment = chat_api.clone_chat(
                "chat-123",
                title="Experiment: Alternative Approach"
            )

            # Verify independence
            original = chat_api.get_chat("chat-123")
            cloned = chat_api.get_chat(cloned['id'])
            # Modifying cloned does not affect original
            ```

        Clone Behavior:
            - Complete deep copy of message tree
            - New chat_id generated
            - Independent: Changes don't affect original
            - Tags NOT copied (start with empty tags)
            - Folder assignment NOT copied

        Metadata:
            - originalChatId field references source
            - Clone chain preserved: Can clone a clone
            - Useful for tracking conversation lineage

        Use Cases:
            - Branch conversation from earlier point
            - Create chat templates (clone and modify)
            - Experiment with different responses
            - Share conversation starting point

        Notes:
            - Requires read access to source chat
            - Clone owned by current user
            - Original chat unaffected
            - Share status NOT copied

        See Also:
            - clone_shared_chat(): Clone from public share link
            - update_chat(): Modify cloned chat
        """
        payload = {}
        if title:
            payload["title"] = title
        return self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}/clone", json_data=payload
        )

    def clone_shared_chat(self, share_id: str) -> Optional[Dict[str, Any]]:
        """Clone a publicly shared chat to your own collection.

        Creates a copy of a shared chat (identified by share_id) owned by current user.
        This allows anyone to copy interesting shared conversations.
        Public operation - no authentication required.

        Official Backend Reference:
            - routers/chats.py:668-683 @router.post("/{id}/clone/shared")

        Args:
            share_id (str): Public share identifier (not chat_id)
                           Extract from share URL: .../share/{share_id}

        Returns:
            Optional[Dict]: Newly created chat object owned by current user:
            {
                "id": str,  # New chat ID (your copy)
                "user_id": str,  # Your user ID
                "title": str,  # Same title as original
                "chat": {  # Complete message history copy
                    "history": {...},
                    "originalChatId": str  # Reference to shared chat
                },
                "created_at": int,
                ...
            }
            Returns None if share_id invalid or cloning fails.

        Example:
            ```python
            # Clone from public share link
            # Share URL: https://openwebui.com/share/abc123xyz
            share_id = "abc123xyz"

            my_copy = chat_api.clone_shared_chat(share_id)
            if my_copy:
                print(f"Cloned to: {my_copy['id']}")
                print(f"Title: {my_copy['title']}")

                # Now you can modify your copy
                chat_api.update_chat(my_copy['id'], {
                    "chat": {
                        "title": "My Modified Version"
                    }
                })

            # Clone and add to folder
            cloned = chat_api.clone_shared_chat("xyz789")
            if cloned:
                chat_api.set_chat_folder(cloned['id'], "templates")
            ```

        Clone Behavior:
            - Complete deep copy of message tree
            - Owned by current user (not original owner)
            - Independent: Modifications don't affect original
            - originalChatId preserved for attribution

        Use Cases:
            - Save interesting shared conversations
            - Build chat template library
            - Learn from shared examples
            - Fork conversation for experimentation

        Notes:
            - Public endpoint (no auth required)
            - Original chat must be currently shared
            - Tags NOT copied
            - Folder NOT assigned (starts unfoldered)

        See Also:
            - get_shared_chat(): View shared chat before cloning
            - clone_chat(): Clone your own chats
            - share_chat(): Share your chats
        """
        return self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{share_id}/clone/shared"
        )

    def share_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Create or regenerate a public share link for a chat.

        Generates a shareable public URL that allows anyone with the link
        to view the chat (read-only). Updates share_id if already shared.
        Useful for sharing conversations externally.

        Official Backend Reference:
            - routers/chats.py:686-712 @router.post("/{id}/share")

        Args:
            chat_id (str): Chat identifier to share

        Returns:
            Optional[Dict]: Updated chat object with share information:
            {
                "id": str,
                "title": str,
                "share_id": str,  # Public share identifier
                "share_url": str,  # Full shareable URL
                ...
            }
            Returns None if sharing fails.

        Example:
            ```python
            # Share a chat
            result = chat_api.share_chat("chat-123")
            if result:
                share_url = result.get('share_url')
                print(f"Share link: {share_url}")
                # Example: https://openwebui.com/share/abc123

            # Share and send via email
            result = chat_api.share_chat("chat-456")
            if result:
                send_email(
                    to="colleague@example.com",
                    subject="Check out this conversation",
                    body=f"View chat: {result['share_url']}"
                )
            ```

        Share Behavior:
            - Generates unique share_id (if not already shared)
            - Updates share_id if already shared (new link)
            - Link valid until unshare_chat() called
            - Read-only access for viewers

        Access Control:
            - Requires share permission (backend setting)
            - Owner can always share their chats
            - Shared chats publicly accessible
            - No authentication required for viewers

        Security Considerations:
            - Share link is publicly accessible
            - Anyone with link can view entire chat history
            - Consider sensitive information before sharing
            - Regenerate link to revoke old shares

        Notes:
            - Share persists across chat updates
            - Archived chats can still be shared
            - Deleted chats: Share link becomes invalid

        See Also:
            - unshare_chat(): Revoke share link
            - get_shared_chat(): View shared chat
            - clone_shared_chat(): Copy shared chat
        """
        return self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}/share"
        )

    def unshare_chat(self, chat_id: str) -> bool:
        """Revoke public share link for a chat (make private).

        Removes the share_id from a chat, making it private again.
        Previously shared links become invalid immediately.
        This is the reverse operation of share_chat().

        Official Backend Reference:
            - routers/chats.py:715-729 @router.delete("/{id}/share")

        Args:
            chat_id (str): Chat identifier to unshare

        Returns:
            bool: True if unshare successful, False on error

        Example:
            ```python
            # Share then unshare
            result = chat_api.share_chat("chat-123")
            share_url = result['share_url']
            print(f"Shared: {share_url}")

            # Revoke access
            if chat_api.unshare_chat("chat-123"):
                print("Share link revoked")
                # Old share_url now returns 404

            # Verify unshared
            chat = chat_api.get_chat("chat-123")
            assert chat['share_id'] is None
            ```

        Effects:
            - Removes share_id from chat
            - Existing share links return 404
            - Chat becomes private (owner-only access)

        Use Cases:
            - Revoke accidental shares
            - Make private after time-limited sharing
            - Security: Revoke compromised links

        Notes:
            - Immediate effect: Links invalid instantly
            - Can re-share with new link via share_chat()
            - Does not affect chat content or visibility to owner

        See Also:
            - share_chat(): Create share link
            - get_shared_chat(): View shared chat
        """
        resp = self.base_client._make_request(
            "DELETE", f"/api/v1/chats/{chat_id}/share"
        )
        return resp is not None and resp.status_code == 200

    def get_shared_chat(self, share_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a publicly shared chat by its share ID.

        Fetches a chat using its public share identifier (not the chat_id).
        This endpoint is publicly accessible - no authentication required.
        Used for viewing shared conversations via public links.

        Official Backend Reference:
            - routers/chats.py:732-742 @router.get("/share/{share_id}")

        Args:
            share_id (str): Public share identifier (from share_url)
                           Example: "abc123xyz" from ".../share/abc123xyz"

        Returns:
            Optional[Dict]: Shared chat object:
            {
                "id": str,  # Original chat_id
                "title": str,
                "chat": {  # Full chat data
                    "history": {...},
                    "models": [...]
                },
                "created_at": int,
                "updated_at": int,
                # Sensitive fields may be filtered
            }
            Returns None if share_id invalid or chat unshared.

        Example:
            ```python
            # View a shared chat (from public link)
            share_id = "abc123xyz"  # Extracted from share URL
            chat = chat_api.get_shared_chat(share_id)

            if chat:
                print(f"Title: {chat['title']}")
                messages = chat['chat']['history']['messages']
                print(f"Messages: {len(messages)}")
            else:
                print("Share link invalid or revoked")

            # Clone shared chat to own collection
            cloned = chat_api.clone_shared_chat(share_id)
            ```

        Access:
            - Public endpoint (no auth required)
            - Read-only access
            - Cannot modify shared chat

        Privacy:
            - Only returns chat if currently shared
            - Unshared chats: Returns None
            - Deleted chats: Returns None

        Notes:
            - share_id ≠ chat_id (different identifiers)
            - Multiple shares of same chat have same share_id
            - Share must be active (not unshared)

        See Also:
            - share_chat(): Create share link
            - clone_shared_chat(): Copy shared chat
            - unshare_chat(): Revoke sharing
        """
        return self.base_client._get_json_response(
            "GET", f"/api/v1/chats/share/{share_id}"
        )

    # =================================================================
    # Chat Metadata (Tags, Folders)
    # =================================================================

    def get_chat_tags(self, chat_id: str) -> List[Dict[str, Any]]:
        """Retrieve all tags associated with a specific chat.

        Returns the complete list of tags assigned to a chat.
        Useful for displaying chat categorization or filtering.

        Official Backend Reference:
            - routers/chats.py:745-778 @router.get("/{id}/tags")

        Args:
            chat_id (str): Chat identifier

        Returns:
            List[Dict]: Tag objects:
            [
                {
                    "id": str,  # Tag ID
                    "name": str,  # Tag name
                    "user_id": str,
                    "data": {...}  # Optional metadata
                },
                ...
            ]
            Returns empty list if no tags or on error.

        Example:
            ```python
            # Get chat tags
            tags = chat_api.get_chat_tags("chat-123")
            tag_names = [t['name'] for t in tags]
            print(f"Tags: {', '.join(tag_names)}")

            # Check for specific tag
            has_work_tag = any(t['name'] == 'work' for t in tags)
            if has_work_tag:
                print("This is a work-related chat")

            # Compare tags across chats
            chat1_tags = set(t['name'] for t in chat_api.get_chat_tags("chat-1"))
            chat2_tags = set(t['name'] for t in chat_api.get_chat_tags("chat-2"))
            common = chat1_tags & chat2_tags
            print(f"Common tags: {common}")
            ```

        Notes:
            - Fast: Indexed database query
            - Empty list for untagged chats (not an error)
            - Tag order not guaranteed

        See Also:
            - add_chat_tag(): Add tag to chat
            - delete_chat_tag(): Remove tag from chat
            - get_all_user_tags(): List all available tags
        """
        resp = self.base_client._get_json_response(
            "GET", f"/api/v1/chats/{chat_id}/tags"
        )
        return resp if isinstance(resp, list) else []

    def add_chat_tag(self, chat_id: str, tag_name: str) -> List[Dict[str, Any]]:
        """Add a tag to a chat for categorization.

        Tags enable chat organization and filtering.
        Creates the tag automatically if it doesn't exist.
        Tags are shared across all user's chats.

        Official Backend Reference:
            - routers/chats.py:781-809 @router.post("/{id}/tags")

        Args:
            chat_id (str): Chat identifier to tag
            tag_name (str): Tag name (e.g., "work", "research", "tutorial")

        Returns:
            List[Dict]: All current tags on this chat:
            [
                {
                    "id": str,  # Tag ID
                    "name": str,  # Tag name
                    "user_id": str,
                    ...
                },
                ...
            ]
            Returns empty list on error.

        Example:
            ```python
            # Add tags to organize chat
            tags = chat_api.add_chat_tag("chat-123", "work")
            tags = chat_api.add_chat_tag("chat-123", "python")
            print(f"Tags: {[t['name'] for t in tags]}")
            # Output: ['work', 'python']

            # Tag multiple chats with same tag
            for chat_id in project_chats:
                chat_api.add_chat_tag(chat_id, "project-alpha")

            # Find all chats with tag
            work_chats = chat_api.get_chats_by_tag("work")
            ```

        Tag Behavior:
            - Case-sensitive: "Work" ≠ "work"
            - Duplicates ignored: Adding same tag twice has no effect
            - Auto-create: Tag created if doesn't exist
            - Shared: Same tag can be on multiple chats

        Use Cases:
            - Categorize: Group chats by topic
            - Filter: Quick access to related chats
            - Search: Use "tag:name" in search

        Notes:
            - Tags persist until explicitly removed
            - Archived chats: Tags removed on archive
            - Deleted chats: Tags cleaned up automatically

        See Also:
            - delete_chat_tag(): Remove specific tag
            - get_chat_tags(): List chat's tags
            - get_chats_by_tag(): Find chats with tag
        """
        payload = {"name": tag_name}
        resp = self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}/tags", json_data=payload
        )
        return resp if isinstance(resp, list) else []

    def delete_chat_tag(self, chat_id: str, tag_name: str) -> List[Dict[str, Any]]:
        """Remove a tag from a chat.

        Removes the association between a chat and a tag.
        If this was the only chat using the tag, the tag is deleted entirely.
        This is a cleanup-aware operation.

        Official Backend Reference:
            - routers/chats.py:812-842 @router.delete("/{id}/tags")

        Args:
            chat_id (str): Chat identifier
            tag_name (str): Tag name to remove

        Returns:
            List[Dict]: Remaining tags on this chat:
            [
                {"id": str, "name": str, ...},
                ...
            ]
            Returns empty list if no tags remain or on error.

        Example:
            ```python
            # Add and then remove a tag
            chat_api.add_chat_tag("chat-123", "draft")
            remaining = chat_api.delete_chat_tag("chat-123", "draft")
            print(f"Remaining tags: {[t['name'] for t in remaining]}")

            # Remove tag from multiple chats
            outdated_chats = chat_api.get_chats_by_tag("old-project")
            for chat in outdated_chats:
                chat_api.delete_chat_tag(chat['id'], "old-project")
            # Tag deleted after last usage
            ```

        Cleanup Behavior:
            - If last chat: Tag record deleted from database
            - If shared: Tag preserved for other chats
            - Non-existent tag: Silently succeeds (idempotent)

        Notes:
            - Case-sensitive: "Work" ≠ "work"
            - Idempotent: Removing non-existent tag is OK
            - Fast: Single database operation

        See Also:
            - delete_all_chat_tags(): Remove all tags from chat
            - add_chat_tag(): Add tag to chat
            - get_all_user_tags(): List all available tags
        """
        payload = {"name": tag_name}
        # Note: DELETE with JSON body, not common but supported by FastAPI
        resp = self.base_client._make_request(
            "DELETE", f"/api/v1/chats/{chat_id}/tags", json=payload
        )
        if resp and resp.status_code == 200:
            return resp.json()
        return []

    def delete_all_chat_tags(self, chat_id: str) -> bool:
        """Remove all tags from a chat (bulk tag removal).

        Efficiently removes all tag associations from a chat in one operation.
        Cleanup-aware: Deletes orphaned tags (tags used only by this chat).
        Faster than calling delete_chat_tag() for each tag.

        Official Backend Reference:
            - routers/chats.py:845-864 @router.delete("/{id}/tags/all")

        Args:
            chat_id (str): Chat identifier

        Returns:
            bool: True if successful, False on error

        Example:
            ```python
            # Remove all tags from chat
            success = chat_api.delete_all_chat_tags("chat-123")
            if success:
                print("All tags removed")

            # Verify removal
            tags = chat_api.get_chat_tags("chat-123")
            assert len(tags) == 0

            # Bulk tag reset (remove then re-add)
            chat_api.delete_all_chat_tags("chat-456")
            for tag in ["new-tag1", "new-tag2"]:
                chat_api.add_chat_tag("chat-456", tag)
            ```

        Cleanup Behavior:
            - Removes all chat-tag associations
            - Deletes tags if this was their only chat
            - Shared tags (used by other chats) preserved

        Use Cases:
            - Reset chat categorization
            - Prepare chat for re-tagging
            - Clean up before deletion

        Notes:
            - Atomic operation (all or nothing)
            - Idempotent: Safe to call on untagged chats
            - Faster than individual tag deletions

        See Also:
            - delete_chat_tag(): Remove single tag
            - add_chat_tag(): Add tags after removal
        """
        resp = self.base_client._make_request(
            "DELETE", f"/api/v1/chats/{chat_id}/tags/all"
        )
        return resp is not None and resp.status_code == 200

    def get_all_user_tags(self) -> List[Dict[str, Any]]:
        """List all tags used by current user across all chats.

        Returns complete tag collection for the authenticated user.
        Useful for tag selection UI, autocomplete, and analytics.
        Shows only tags currently in use (attached to at least one chat).

        Official Backend Reference:
            - routers/chats.py:900-913 @router.get("/all/tags")

        Returns:
            List[Dict]: All user's tags:
            [
                {
                    "id": str,
                    "name": str,
                    "user_id": str,
                    "count": int,  # Number of chats with this tag
                    "data": {...}  # Optional metadata
                },
                ...
            ]
            Returns empty list if user has no tags or on error.

        Example:
            ```python
            # List all available tags
            all_tags = chat_api.get_all_user_tags()
            print("Available tags:")
            for tag in all_tags:
                count = tag.get('count', 0)
                print(f"  - {tag['name']} ({count} chats)")

            # Tag autocomplete/suggestions
            tag_names = [t['name'] for t in all_tags]
            user_input = "wo"  # User typing...
            suggestions = [t for t in tag_names if t.startswith(user_input)]
            # Suggests: ['work', 'workshop']

            # Find most used tags
            sorted_tags = sorted(
                all_tags,
                key=lambda t: t.get('count', 0),
                reverse=True
            )
            top_5 = sorted_tags[:5]
            print("Most used tags:", [t['name'] for t in top_5])
            ```

        Tag Lifecycle:
            - Created: When first added to any chat
            - Listed: While attached to at least one chat
            - Deleted: When removed from last chat

        Use Cases:
            - Tag selection UI (dropdown/autocomplete)
            - Tag analytics and statistics
            - Bulk tag operations
            - Tag management interface

        Notes:
            - Only shows user's own tags (not global)
            - Excludes tags from other users
            - Count field useful for popularity sorting
            - Ordered alphabetically by name

        See Also:
            - get_chats_by_tag(): Find chats with specific tag
            - add_chat_tag(): Create/assign tags
        """
        resp = self.base_client._get_json_response("GET", "/api/v1/chats/all/tags")
        return resp if isinstance(resp, list) else []

    def get_chats_by_tag(
        self, tag_name: str, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Find all chats tagged with a specific tag.

        Retrieves chats filtered by tag name with pagination support.
        Useful for viewing all chats in a category.
        Automatically cleans up tag if no chats found.

        Official Backend Reference:
            - routers/chats.py:867-897 @router.post("/tags")

        Args:
            tag_name (str): Tag name to filter by (case-sensitive)
            skip (int): Number of results to skip (for pagination)
                       Default: 0 (start from beginning)
            limit (int): Maximum results to return
                        Default: 50

        Returns:
            List[Dict]: Matching chat objects (lightweight):
            [
                {
                    "id": str,
                    "title": str,
                    "updated_at": int,
                    "meta": {"tags": [...]},
                    ...
                },
                ...
            ]
            Returns empty list if no matches or tag doesn't exist.

        Example:
            ```python
            # Get all work-related chats
            work_chats = chat_api.get_chats_by_tag("work")
            print(f"Work chats: {len(work_chats)}")

            # Paginated retrieval
            first_batch = chat_api.get_chats_by_tag("python", skip=0, limit=10)
            second_batch = chat_api.get_chats_by_tag("python", skip=10, limit=10)

            # Process all chats with tag
            skip = 0
            while True:
                batch = chat_api.get_chats_by_tag("research", skip=skip, limit=50)
                if not batch:
                    break
                for chat in batch:
                    process_chat(chat)
                skip += 50
            ```

        Cleanup Behavior:
            - If no chats found: Tag is deleted from system
            - This prevents orphaned tags
            - Empty result triggers cleanup

        Notes:
            - Case-sensitive matching
            - Excludes archived chats
            - Ordered by updated_at DESC

        See Also:
            - search_chats(): Search with "tag:name" query
            - get_all_user_tags(): List all available tags
            - add_chat_tag(): Add tag to chat
        """
        payload = {"name": tag_name, "skip": skip, "limit": limit}
        resp = self.base_client._get_json_response(
            "POST", "/api/v1/chats/tags", json_data=payload
        )
        return resp if isinstance(resp, list) else []

    def set_chat_folder(
        self, chat_id: str, folder_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Assign a chat to a folder or remove from folder.

        Moves chat into specified folder for organization.
        Pass None as folder_id to remove chat from current folder.
        Supports moving between folders.

        Official Backend Reference:
            - routers/chats.py:916-944 @router.post("/{id}/folder")

        Args:
            chat_id (str): Chat identifier to move
            folder_id (Optional[str]): Target folder ID, or None to unassign

        Returns:
            Optional[Dict]: Updated chat object:
            {
                "id": str,
                "title": str,
                "folder_id": str | None,  # New assignment
                "updated_at": int,
                ...
            }
            Returns None if operation fails.

        Example:
            ```python
            # Move chat to folder
            work_folder = chat_api.create_folder("Work")
            result = chat_api.set_chat_folder("chat-123", work_folder['id'])
            if result:
                print(f"Moved to: {result['folder_id']}")

            # Remove from folder (unassign)
            result = chat_api.set_chat_folder("chat-123", None)
            assert result['folder_id'] is None

            # Move between folders
            projects = chat_api.create_folder("Projects")
            archived = chat_api.create_folder("Archived")

            # Start in Projects
            chat_api.set_chat_folder("chat-456", projects['id'])
            # Later move to Archived
            chat_api.set_chat_folder("chat-456", archived['id'])

            # Bulk folder assignment
            folder_id = work_folder['id']
            for chat_id in work_chat_ids:
                chat_api.set_chat_folder(chat_id, folder_id)
            ```

        Folder Behavior:
            - Chat can be in 0 or 1 folder (not multiple)
            - Moving replaces previous folder assignment
            - Folder must exist (will fail for invalid folder_id)
            - None removes from any folder

        Validation:
            - folder_id must be valid folder ID or None
            - User must own both chat and folder
            - Folder must not be deleted

        Notes:
            - Moving doesn't affect chat content
            - Folder assignment persists
            - Archived chats can be in folders
            - Deleting folder unassigns chats (not deleted)

        See Also:
            - create_folder(): Create folders
            - get_chats_by_folder(): List folder contents
            - list_folders(): List all folders
        """
        payload = {"folder_id": folder_id}
        return self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}/folder", json_data=payload
        )

    def get_chats_by_folder(self, folder_id: str) -> List[Dict[str, Any]]:
        """Retrieve all chats in a folder (including nested folders).

        Returns all chats assigned to specified folder and its subfolders.
        Recursive search through folder hierarchy.
        Returns full chat objects with complete data.

        Official Backend Reference:
            - routers/chats.py:947-963 @router.get("/folder/{folder_id}")

        Args:
            folder_id (str): Folder identifier

        Returns:
            List[Dict]: Chat objects in folder (full data):
            [
                {
                    "id": str,
                    "title": str,
                    "folder_id": str,
                    "chat": {"history": {...}, ...},
                    ...
                },
                ...
            ]
            Returns empty list if folder empty or doesn't exist.

        Example:
            ```python
            # Get all chats in folder
            work_chats = chat_api.get_chats_by_folder("folder-123")
            print(f"Work chats: {len(work_chats)}")

            # Process folder contents
            for chat in work_chats:
                print(f"- {chat['title']}")
                message_count = len(chat['chat']['history']['messages'])
                print(f"  ({message_count} messages)")

            # Export folder contents
            chats = chat_api.get_chats_by_folder("projects")
            export_data = {
                'folder': 'projects',
                'chats': chats
            }
            with open('export.json', 'w') as f:
                json.dump(export_data, f)
            ```

        Recursive Search:
            - Includes chats in subfolders
            - Traverses entire folder tree
            - No depth limit

        Notes:
            - Returns full chat objects (can be large)
            - For UI lists, use get_chat_list_by_folder() instead
            - Excludes archived chats
            - Empty folder returns [] (not error)

        See Also:
            - get_chat_list_by_folder(): Lightweight paginated list
            - set_chat_folder(): Assign chats to folder
            - list_folders(): List all folders
        """
        resp = self.base_client._get_json_response(
            "GET", f"/api/v1/chats/folder/{folder_id}"
        )
        return resp if isinstance(resp, list) else []

    def get_chat_list_by_folder(
        self, folder_id: str, page: int = 1
    ) -> List[Dict[str, Any]]:
        """Get paginated lightweight chat list for a folder (UI optimization).

        Returns simplified chat objects without message history.
        Optimized for UI chat lists - much faster than get_chats_by_folder().
        Paginated for performance with large folders.

        Official Backend Reference:
            - routers/chats.py:966-990 @router.get("/folder/{folder_id}/list")

        Args:
            folder_id (str): Folder identifier
            page (int): Page number (1-indexed), 60 chats per page
                       Default: 1

        Returns:
            List[Dict]: Lightweight chat summaries:
            [
                {
                    "id": str,
                    "title": str,
                    "updated_at": int,
                    "created_at": int,
                    "folder_id": str,
                    # No chat.history field!
                },
                ...
            ]
            Returns empty list if folder empty or page out of range.

        Example:
            ```python
            # Get first page of folder
            chats = chat_api.get_chat_list_by_folder("folder-123", page=1)
            for chat in chats:
                print(f"{chat['title']}: {chat['updated_at']}")

            # Paginate through large folder
            page = 1
            all_chats = []
            while True:
                batch = chat_api.get_chat_list_by_folder(
                    "large-folder",
                    page=page
                )
                if not batch:
                    break
                all_chats.extend(batch)
                page += 1

            print(f"Total chats: {len(all_chats)}")

            # UI chat list rendering
            def render_folder_list(folder_id):
                chats = chat_api.get_chat_list_by_folder(folder_id)
                for chat in chats:
                    display_chat_preview(
                        title=chat['title'],
                        last_updated=chat['updated_at']
                    )
            ```

        Performance Comparison:
            - get_chats_by_folder(): Full data, slow for 100+ chats
            - get_chat_list_by_folder(): Lightweight, fast for 1000+ chats
            - Use list variant for UI, full variant for export

        Pagination:
            - 60 chats per page (backend configured)
            - Ordered by updated_at DESC
            - Empty page returns [] (not error)

        Notes:
            - Does NOT include subfolders (direct children only)
            - No message history loaded
            - For full data, call get_chat() for each chat

        See Also:
            - get_chats_by_folder(): Full chat objects (slower)
            - list_chats(): Similar lightweight list (all chats)
        """
        params = {"page": page}
        resp = self.base_client._get_json_response(
            "GET", f"/api/v1/chats/folder/{folder_id}/list", params=params
        )
        return resp if isinstance(resp, list) else []

    # =================================================================
    # Chat Import/Export
    # =================================================================

    def import_chats(self, chats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Import multiple chats in bulk (restore/migrate).

        Uploads and creates multiple chats in one operation.
        Useful for restoring backups, migrating from other systems,
        or batch chat creation. Validates and imports each chat.

        Official Backend Reference:
            - routers/chats.py:993-1036 @router.post("/import")

        Args:
            chats (List[Dict]): List of complete chat objects to import:
                [
                    {
                        "id": str,  # Optional: will be reassigned if conflicts
                        "title": str,
                        "chat": {
                            "history": {...},
                            "models": [...]
                        },
                        "created_at": int,
                        "updated_at": int,
                        # Other fields...
                    },
                    ...
                ]

        Returns:
            List[Dict]: Successfully imported chat objects:
            [
                {
                    "id": str,  # New/reassigned ID
                    "title": str,
                    "user_id": str,  # Current user
                    ...
                },
                ...
            ]
            Empty list if all imports fail.

        Example:
            ```python
            # Restore from backup
            with open('backup.json', 'r') as f:
                backup_chats = json.load(f)

            imported = chat_api.import_chats(backup_chats)
            print(f"Imported {len(imported)}/{len(backup_chats)} chats")

            # Migrate from export
            exported = chat_api.get_all_chats()
            # ... save to file ...
            # Later, on different account:
            imported = chat_api.import_chats(exported)

            # Partial import with error handling
            chats_to_import = load_chats_from_file()
            imported = chat_api.import_chats(chats_to_import)

            failed_count = len(chats_to_import) - len(imported)
            if failed_count > 0:
                print(f"Warning: {failed_count} chats failed to import")
            ```

        Import Behavior:
            - Validates each chat structure
            - Skips invalid chats (continues with others)
            - Reassigns IDs if conflicts exist
            - Imports to current user (not original owner)
            - Preserves message history and metadata

        Validation:
            - Required fields: title, chat.history
            - Valid message structure
            - Valid model references
            - Timestamps within reasonable range

        ID Handling:
            - Existing IDs may be reassigned to avoid conflicts
            - Check returned IDs for actual assignments
            - Parent/child message IDs preserved within chat

        Warnings:
            - Large imports (100+ chats) may timeout
            - Consider batching: 50 chats per call
            - No progress feedback during import
            - Failed chats silently skipped

        Notes:
            - Atomic per chat (each chat independent)
            - Folder assignments NOT imported (assign after)
            - Tags NOT imported (add separately)
            - Share status NOT preserved

        See Also:
            - get_all_chats(): Export for backup
            - create_chat(): Import single chat
        """
        payload = {"chats": chats}
        resp = self.base_client._get_json_response(
            "POST", "/api/v1/chats/import", json_data=payload
        )
        return resp if isinstance(resp, list) else []

    # =================================================================
    # Folders
    # =================================================================

    def create_folder(
        self, name: str, parent_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a folder for organizing chats.

        Folders provide hierarchical chat organization.
        Supports nested folders via parent_id.
        All chats in a folder can be retrieved together.

        Official Backend Reference:
            - routers/folders.py:41-70 @router.post("/")

        Args:
            name (str): Folder display name (e.g., "Work Projects")
            parent_id (Optional[str]): Parent folder ID for nested structure
                                      None creates top-level folder

        Returns:
            Optional[Dict]: Created folder object:
            {
                "id": str,  # Generated folder ID
                "name": str,
                "parent_id": str | None,
                "user_id": str,
                "created_at": int,
                "updated_at": int,
                "is_expanded": bool,  # UI state
                "items": []  # Child items (folders/chats)
            }
            Returns None if creation fails.

        Example:
            ```python
            # Create top-level folder
            work = chat_api.create_folder("Work")
            if work:
                print(f"Created folder: {work['id']}")

            # Create nested folder hierarchy
            projects = chat_api.create_folder(
                "Projects",
                parent_id=work['id']
            )

            client_a = chat_api.create_folder(
                "Client A",
                parent_id=projects['id']
            )

            # Assign chat to folder
            chat_api.set_chat_folder("chat-123", client_a['id'])

            # Folder structure:
            # Work/
            #   Projects/
            #     Client A/
            #       [chat-123]
            ```

        Folder Features:
            - Hierarchical: Unlimited nesting depth
            - Movable: Can change parent_id
            - Deletable: Deleting folder unassigns chats (not deleted)
            - UI State: is_expanded persisted

        Validation:
            - name required (non-empty)
            - parent_id must exist if provided
            - Duplicate names allowed

        Notes:
            - Folders are user-specific
            - No folder permissions (inherit user permissions)
            - Deleting folder doesn't delete chats

        See Also:
            - list_folders(): List all folders
            - set_chat_folder(): Assign chat to folder
            - get_chats_by_folder(): List folder contents
        """
        payload = {"name": name}
        if parent_id:
            payload["parent_id"] = parent_id
        return self.base_client._get_json_response(
            "POST", "/api/v1/folders/", json_data=payload
        )

    def list_folders(self) -> List[Dict[str, Any]]:
        """List all folders owned by current user (entire folder tree).

        Returns complete folder hierarchy including nested structures.
        Each folder includes metadata and child items.
        Used for building folder navigation UI.

        Official Backend Reference:
            - routers/folders.py:73-102 @router.get("/")

        Returns:
            List[Dict]: Folder objects with hierarchy:
            [
                {
                    "id": str,
                    "name": str,
                    "parent_id": str | None,
                    "user_id": str,
                    "created_at": int,
                    "updated_at": int,
                    "is_expanded": bool,  # UI state
                    "items": [],  # Child folders/chats
                    "type": "folder"
                },
                ...
            ]
            Returns empty list if no folders or on error.

        Example:
            ```python
            # List all folders
            folders = chat_api.list_folders()
            print(f"Total folders: {len(folders)}")

            # Find top-level folders
            top_level = [f for f in folders if f['parent_id'] is None]
            print("Top-level folders:")
            for folder in top_level:
                print(f"- {folder['name']}")

            # Build folder tree
            def build_tree(folders):
                tree = {}
                for folder in folders:
                    if folder['parent_id'] is None:
                        tree[folder['id']] = {
                            'name': folder['name'],
                            'children': []
                        }
                return tree

            # Find folder by name
            def find_folder(name):
                for folder in folders:
                    if folder['name'] == name:
                        return folder
                return None

            work_folder = find_folder("Work")
            ```

        Hierarchy Structure:
            - parent_id=None: Top-level folders
            - parent_id set: Nested folders
            - Unlimited nesting depth

        Use Cases:
            - Render folder tree UI
            - Folder navigation
            - Folder management interface
            - Chat organization overview

        Notes:
            - Returns all folders (no pagination)
            - Includes empty folders
            - items field may be empty or populated
            - is_expanded is UI state hint

        See Also:
            - create_folder(): Create new folders
            - get_chats_by_folder(): Get folder contents
        """
        resp = self.base_client._get_json_response("GET", "/api/v1/folders/")
        return resp if isinstance(resp, list) else []

    # =================================================================
    # Files
    # =================================================================

    def upload_file(self, file_path: str) -> Optional[FileDict]:
        """Upload a file for use in multimodal chat or RAG.

        Uploads file to Open WebUI storage and returns file metadata.
        Uploaded files can be attached to messages for:
        - Multimodal input (images for vision models)
        - RAG (document question-answering)
        - Code analysis
        - Data processing

        Official Backend Reference:
            - routers/files.py:54-145 @router.post("/")

        Args:
            file_path (str): Absolute path to file on local filesystem

        Returns:
            Optional[FileDict]: File metadata object:
            {
                "id": str,  # Unique file identifier
                "filename": str,  # Original filename
                "path": str,  # Server storage path
                "size": int,  # File size in bytes
                "mime_type": str,  # MIME type (image/png, application/pdf, etc.)
                "user_id": str,
                "created_at": int,
                "meta": {  # Extracted metadata
                    "content_type": str,
                    "size": int,
                    "name": str
                }
            }
            Returns None if upload fails.

        Example:
            ```python
            # Upload image for vision model
            file = chat_api.upload_file("/path/to/image.png")
            if file:
                print(f"Uploaded: {file['id']}")

                # Use in multimodal chat
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What's in this image?"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"file:{file['id']}"}
                            }
                        ]
                    }
                ]
                response = chat_api.completion({
                    "model": "gpt-4-vision",
                    "messages": messages
                })

            # Upload document for RAG
            pdf = chat_api.upload_file("/path/to/document.pdf")
            if pdf:
                # Use in RAG-enabled chat
                response = chat_api.completion({
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": "Summarize this PDF"}],
                    "files": [{"id": pdf['id'], "name": pdf['filename']}]
                })
            ```

        Supported File Types:
            - Images: PNG, JPEG, GIF, WebP (for vision models)
            - Documents: PDF, TXT, MD, DOC, DOCX (for RAG)
            - Code: PY, JS, TS, etc. (for code analysis)
            - Data: CSV, JSON, XML (for data processing)

        Limitations:
            - Max size: 100MB (configurable in backend)
            - Some types require specific model support
            - Large files may timeout on slow connections

        Validation:
            - File must exist and be readable
            - Valid MIME type
            - Within size limits

        Error Handling:
            - Returns None on:
              * File not found
              * Permission denied
              * Network error
              * Size limit exceeded
            - Logs detailed error messages

        Notes:
            - Files stored on server
            - File ID used in subsequent API calls
            - Files may be cleaned up after inactivity
            - No automatic deletion on chat delete

        See Also:
            - completion(): Use uploaded files in chat
            - ChatPayloads.build_user_message(): Attach files to messages
        """
        try:
            if not file_path or not isinstance(file_path, str):
                logger.error(f"Invalid file_path: {file_path}")
                return None

            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None

            if not os.path.isfile(file_path):
                logger.error(f"Path is not a file: {file_path}")
                return None

            # Check file size (max 100MB)
            file_size = os.path.getsize(file_path)
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                logger.error(
                    f"File too large: {file_size} bytes (max {max_size} bytes)"
                )
                return None

            with open(file_path, "rb") as f:
                files = {"file": f}
                response = self.base_client._make_request(
                    "POST", "/api/v1/files/", files=files
                )

                if not response:
                    logger.error(f"Upload request returned None for file: {file_path}")
                    return None

                if response.status_code != 200:
                    logger.error(
                        f"Upload failed with status {response.status_code} for file: {file_path}"
                    )
                    return None

                return response.json()

        except PermissionError as e:
            logger.error(f"Permission denied reading file {file_path}: {e}")
            return None
        except OSError as e:
            logger.error(f"OS error reading file {file_path}: {e}", exc_info=True)
            return None
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Upload request failed for file {file_path}: {e}", exc_info=True
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error uploading file {file_path}: {e}", exc_info=True
            )
            return None
