"""Chat Payload Builder - Official Open WebUI Schema Compliance.

This module provides builders for constructing message and chat structures that
exactly match the official Open WebUI backend data models. Understanding these
structures is critical for correct API usage.

Key Data Structures:

1. Message (Graph Node):
   ```python
   {
       "id": str,              # Unique identifier
       "role": "user" | "assistant" | "system",
       "content": str | List[ContentBlock],  # Text or multimodal
       "model": str,           # Model identifier (for assistant)
       "parentId": str | None, # Parent message ID (tree structure)
       "childrenIds": [str],   # Child message IDs
       "timestamp": int,       # Unix timestamp (seconds)
       "files": [...],         # Optional: attached files
       "sources": [...],       # Optional: citation sources
       "info": {...},          # Optional: metadata (tokens, timing)
       "done": bool,           # Optional: completion status
   }
   ```

2. Chat History (Message Tree):
   ```python
   {
       "currentId": str,       # Active leaf node
       "messages": {
           msg_id: message_object,  # Dictionary mapping
           ...
       }
   }
   ```

   Tree Structure:
   - Messages form a directed acyclic graph (DAG)
   - Multiple branches allowed (edit/regenerate creates siblings)
   - currentId points to active conversation path
   - Frontend traverses from currentId back to root via parentId

3. Chat Object:
   ```python
   {
       "title": str,
       "history": ChatHistoryDict,
       "models": [str],        # Model IDs used
       "params": {...}         # Model parameters
   }
   ```

4. Complete Chat (ChatModel):
   ```python
   {
       "id": str,              # Chat UUID
       "user_id": str,
       "title": str,
       "chat": ChatBodyDict,   # Inner chat object
       "folder_id": str | None,
       "meta": {"tags": [], "pinned": bool},
       "created_at": int,
       "updated_at": int
   }
   ```

Multimodal Content Blocks:
   ```python
   # Text only
   content = "Hello world"

   # Multimodal (text + images)
   content = [
       {"type": "text", "text": "Describe this image:"},
       {"type": "image_url", "image_url": {
           "url": "data:image/jpeg;base64,..."
       }}
   ]
   ```

Official Backend Reference:
    - backend/open_webui/models/chats.py (ChatModel, MessageStats)
    - backend/open_webui/main.py:1565-1857 (completion payload)
    - backend/open_webui/utils/middleware.py (payload processing)

Usage Example:
    ```python
    from openwebui_chat_client.modules.chat.payloads import ChatPayloads

    # Build conversation
    user_msg = ChatPayloads.build_user_message(
        content="What is Python?",
        model="gpt-4.1"
    )

    assistant_msg = ChatPayloads.build_assistant_message(
        content="Python is a programming language...",
        model="gpt-4.1",
        parent_id=user_msg["id"],
        done=True
    )

    # Build complete chat payload
    payload = ChatPayloads.build_chat_payload(
        title="Python Discussion",
        messages=[user_msg, assistant_msg],
        current_id=assistant_msg["id"],
        models=["gpt-4.1"]
    )

    # Create chat
    chat_api.create_chat(payload)
    ```

Common Patterns:

1. Linear Conversation:
   ```
   [User] -> [Assistant] -> [User] -> [Assistant]
   ```
   Each message's parentId points to previous message.

2. Branching (Edit/Regenerate):
   ```
   [User] -> [Assistant A]
          -> [Assistant B]
   ```
   Both assistants share same parentId, creating siblings.

3. Multi-turn with Branches:
   ```
   [User 1] -> [Asst 1] -> [User 2] -> [Asst 2A]
                                    -> [Asst 2B]
   ```
   currentId points to active branch (2A or 2B).

See Also:
    - types.py: Type definitions for all structures
    - api.py: API methods consuming these payloads
    - workflow.py: Orchestration using payload builders
"""

from typing import Any, Dict, List, Optional, Union
import uuid
import time
import logging

# Type definitions
from .types import (
    MessageDict,
    ChatHistoryDict,
    ChatBodyDict,
    ChatFormDict,
    CompletionPayloadDict,
    CompletedPayloadDict,
    MessageContent,
    MessageRole,
    MessageID,
    ChatID,
)

logger = logging.getLogger(__name__)


class ChatPayloads:
    """
    Chat Payload Builder - Official Open WebUI Schema Compliance.

    Constructs message and chat structures that match Open WebUI backend models.
    Based on: backend/open_webui/models/chats.py

    Message Structure (Graph-based History):
    - id: unique identifier
    - role: "user" | "assistant" | "system"
    - content: string or content blocks (for multimodal)
    - model: model identifier
    - parentId: parent message id (forms tree structure)
    - childrenIds: list of child message ids
    - timestamp: epoch timestamp (seconds)
    - Optional: files, sources, info, annotation, etc.

    Chat Structure:
    - id: chat identifier
    - title: chat title
    - chat: {
        history: {
            currentId: active message id (leaf node in tree),
            messages: {id: message_object, ...}  # Dictionary mapping
        },
        params: {},  # model parameters
        models: []   # model ids used in chat
      }
    - meta: {tags: [], ...}  # metadata
    - folder_id: optional folder assignment
    """

    @staticmethod
    def build_message(
        role: MessageRole,
        content: MessageContent,
        model: Optional[str] = None,
        parent_id: Optional[MessageID] = None,
        msg_id: Optional[MessageID] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        sources: Optional[List[str]] = None,
        info: Optional[Dict[str, Any]] = None,
        **extra_fields: Any,
    ) -> MessageDict:
        """
        Build a message following Open WebUI schema.

        Args:
            role: "user" | "assistant" | "system"
            content: Message content (string or content blocks for multimodal)
            model: Model identifier (required for assistant messages)
            parent_id: Parent message ID in conversation tree
            msg_id: Optional explicit message ID
            files: List of attached files (images, documents, etc.)
            sources: List of source URLs (for citations)
            info: Additional metadata (tokens, timing, etc.)
            **extra_fields: Additional fields (done, error, code_executions, etc.)

        Returns:
            Message dictionary following official schema

        Official: backend/open_webui/models/chats.py (MessageStats structure)
        """
        try:
            # Validate required fields
            if not role or not isinstance(role, str):
                logger.error(f"Invalid role: {role}")
                raise ValueError(f"Role must be a non-empty string, got: {type(role)}")

            if role not in ["user", "assistant", "system"]:
                logger.warning(
                    f"Unexpected role value: {role}, expected user/assistant/system"
                )

            if content is None:
                logger.error("Content is required but was None")
                raise ValueError("Content cannot be None")

            if not isinstance(content, (str, list)):
                logger.error(f"Invalid content type: {type(content)}")
                raise TypeError(f"Content must be string or list, got: {type(content)}")

            # Validate list content (multimodal)
            if isinstance(content, list):
                for idx, block in enumerate(content):
                    if not isinstance(block, dict):
                        logger.error(
                            f"Content block {idx} is not a dict: {type(block)}"
                        )
                        raise TypeError(
                            f"Content blocks must be dicts, block {idx} is {type(block)}"
                        )

            # Validate optional list fields
            if files is not None and not isinstance(files, list):
                logger.error(f"Files must be a list, got: {type(files)}")
                raise TypeError(f"Files must be a list, got: {type(files)}")

            if sources is not None and not isinstance(sources, list):
                logger.error(f"Sources must be a list, got: {type(sources)}")
                raise TypeError(f"Sources must be a list, got: {type(sources)}")

            if info is not None and not isinstance(info, dict):
                logger.error(f"Info must be a dict, got: {type(info)}")
                raise TypeError(f"Info must be a dict, got: {type(info)}")

            message = {
                "id": msg_id or str(uuid.uuid4()),
                "role": role,
                "content": content,
                "timestamp": int(time.time()),
                "parentId": parent_id,
                "childrenIds": [],
            }

            # Add optional fields
            if model:
                message["model"] = model
            if files:
                message["files"] = files
            if sources:
                message["sources"] = sources
            if info:
                message["info"] = info

            # Add any extra fields (done, error, statusHistory, etc.)
            for key, value in extra_fields.items():
                message[key] = value  # type: ignore[literal-required]

            return message  # type: ignore[return-value]

        except (ValueError, TypeError) as e:
            logger.error(f"Failed to build message: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error building message: {e}", exc_info=True)
            raise

    @staticmethod
    def build_user_message(
        content: MessageContent,
        model: Optional[str] = None,
        parent_id: Optional[MessageID] = None,
        files: Optional[List[Dict[str, Any]]] = None,
    ) -> MessageDict:
        """
        Build user message.

        User messages can be multimodal (text + images).
        Content can be a string or list of content blocks.

        Content blocks format:
        [
            {"type": "text", "text": "..."},
            {"type": "image_url", "image_url": {"url": "..."}}
        ]
        """
        return ChatPayloads.build_message(
            role="user", content=content, model=model, parent_id=parent_id, files=files
        )

    @staticmethod
    def build_assistant_message(
        content: str,
        model: str,
        parent_id: MessageID,
        msg_id: Optional[MessageID] = None,
        sources: Optional[List[str]] = None,
        info: Optional[Dict[str, Any]] = None,
        done: bool = True,
        **extra_fields: Any,
    ) -> MessageDict:
        """
        Build assistant message.

        Assistant messages track completion status, sources, and metadata.
        """
        return ChatPayloads.build_message(
            role="assistant",
            content=content,
            model=model,
            parent_id=parent_id,
            msg_id=msg_id,
            sources=sources,
            info=info,
            done=done,
            **extra_fields,
        )

    @staticmethod
    def build_system_message(
        content: str, msg_id: Optional[MessageID] = None
    ) -> MessageDict:
        """
        Build system message.

        System messages are typically used for instructions/context.
        They don't have a model or parent reference.
        """
        return ChatPayloads.build_message(role="system", content=content, msg_id=msg_id)

    @staticmethod
    def build_chat_history(
        messages: List[MessageDict], current_id: MessageID
    ) -> ChatHistoryDict:
        """Build chat history structure (message tree/graph).

        Converts a list of messages into the official Open WebUI history format,
        which uses a dictionary-based message graph with a currentId pointer.

        Tree Structure Explained:
        - Messages are stored in a flat dictionary (not a list)
        - Each message has parentId (forming parent-child relationships)
        - childrenIds tracks all branches (edit/regenerate creates siblings)
        - currentId points to the "active" message (leaf node in active branch)

        Traversal:
        - Frontend walks from currentId -> parentId -> ... -> root
        - This forms the "active conversation path"
        - Inactive branches (other childrenIds) are preserved but hidden

        Official Backend: backend/open_webui/models/chats.py (ChatBody.history)

        Args:
            messages: List of message objects with id, role, content, parentId, etc.
                     Each message must have valid structure from build_message()
            current_id: ID of the current/active message (leaf node)
                       This defines which conversation branch is active

        Returns:
            History object:
            {
                "currentId": str,  # Active message ID
                "messages": {      # Dictionary mapping
                    msg_id: message_object,
                    ...
                }
            }

        Raises:
            TypeError: If messages is not a list or contains non-dict items
            ValueError: If current_id is empty or not a string
            KeyError: If any message missing "id" field

        Example:
            ```python
            # Build linear conversation
            messages = [
                ChatPayloads.build_user_message("Hello", model="gpt-4.1"),
                ChatPayloads.build_assistant_message(
                    "Hi there!",
                    model="gpt-4.1",
                    parent_id=messages[0]["id"]
                )
            ]

            history = ChatPayloads.build_chat_history(
                messages=messages,
                current_id=messages[-1]["id"]  # Last message is current
            )

            print(history)
            # {
            #     "currentId": "msg-uuid-2",
            #     "messages": {
            #         "msg-uuid-1": {"role": "user", "content": "Hello", ...},
            #         "msg-uuid-2": {"role": "assistant", "content": "Hi there!", ...}
            #     }
            # }

            # Build branching conversation (regenerate)
            user_msg = ChatPayloads.build_user_message("Write a poem")
            asst_msg_1 = ChatPayloads.build_assistant_message(
                "Roses are red...",
                model="gpt-4.1",
                parent_id=user_msg["id"]
            )
            asst_msg_2 = ChatPayloads.build_assistant_message(
                "In the garden of dreams...",  # Alternative response
                model="gpt-4.1",
                parent_id=user_msg["id"]  # Same parent!
            )

            # Update parent's childrenIds
            user_msg["childrenIds"] = [asst_msg_1["id"], asst_msg_2["id"]]

            # Choose active branch via currentId
            history = ChatPayloads.build_chat_history(
                messages=[user_msg, asst_msg_1, asst_msg_2],
                current_id=asst_msg_2["id"]  # Select second response
            )

            # Frontend will show: [user_msg] -> [asst_msg_2]
            # asst_msg_1 is preserved but not displayed
            ```

        Validation:
            - All messages must have unique IDs
            - current_id must exist in messages
            - Parent-child relationships should form valid tree (no cycles)

        Notes:
            - Empty messages list is valid (new chat initialization)
            - Message order in list doesn't matter (tree defined by parentId)
            - Duplicate IDs cause last-wins behavior (should be avoided)
            - childrenIds is optional (can be empty or omitted)

        See Also:
            - build_message(): For creating individual messages
            - build_chat_object(): For wrapping history in complete chat
            - add_child_to_parent(): Helper for maintaining tree structure
        """
        try:
            if not isinstance(messages, list):
                logger.error(f"Messages must be a list, got: {type(messages)}")
                raise TypeError(f"Messages must be a list, got: {type(messages)}")

            if not isinstance(current_id, str):
                logger.error(f"Invalid current_id type: {type(current_id)}")
                raise TypeError(f"current_id must be a string, got: {type(current_id)}")

            # For new chats, empty messages and empty current_id are valid
            if len(messages) == 0:
                return {"currentId": current_id, "messages": {}}

            # Convert list to dictionary mapping with validation
            messages_dict = {}
            for idx, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    logger.error(f"Message {idx} is not a dict: {type(msg)}")
                    raise TypeError(f"Message {idx} must be a dict, got: {type(msg)}")

                if "id" not in msg:
                    logger.error(f"Message {idx} missing 'id' field: {msg}")
                    raise KeyError(f"Message {idx} missing required 'id' field")

                msg_id = msg["id"]
                messages_dict[msg_id] = msg

            # Verify current_id exists in messages (only if current_id is not empty)
            if current_id and current_id not in messages_dict:
                logger.warning(f"current_id '{current_id}' not found in messages")

            return {"currentId": current_id, "messages": messages_dict}

        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Failed to build chat history: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error building chat history: {e}", exc_info=True)
            raise

    @staticmethod
    def build_chat_object(
        title: str,
        messages: List[MessageDict],
        current_id: MessageID,
        models: Optional[List[str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> ChatBodyDict:
        """Build the inner chat object (chat.chat field).

        Constructs the core chat data structure that represents the conversation.
        This is the "chat" field within ChatModel and ChatForm payloads.
        Wraps message history with metadata like title, models, and parameters.

        Official Backend Reference:
            - backend/open_webui/models/chats.py (ChatBody class)

        Args:
            title (str): Chat title (user-visible name)
            messages (List[MessageDict]): Message objects with full structure
            current_id (MessageID): ID of current/active message (leaf node)
            models (Optional[List[str]]): Model IDs used in conversation
                                         Example: ["gpt-4.1", "gemini-2.5-flash"]
            params (Optional[Dict[str, Any]]): Model parameters
                                              Example: {"temperature": 0.7, "max_tokens": 500}

        Returns:
            ChatBodyDict: Chat object structure:
            {
                "title": str,
                "history": {
                    "currentId": str,
                    "messages": {msg_id: message_object}
                },
                "models": [str, ...],  # If provided
                "params": {...}        # If provided
            }

        Example:
            ```python
            # Build simple chat object
            messages = [
                ChatPayloads.build_user_message("Hello"),
                ChatPayloads.build_assistant_message(
                    "Hi!",
                    model="gpt-4.1",
                    parent_id=messages[0]["id"]
                )
            ]

            chat_obj = ChatPayloads.build_chat_object(
                title="Friendly Chat",
                messages=messages,
                current_id=messages[-1]["id"],
                models=["gpt-4.1"],
                params={"temperature": 0.7}
            )

            # Use in complete payload
            payload = {"chat": chat_obj}
            chat = chat_api.create_chat(payload)
            ```

        Structure Purpose:
            - Outer ChatModel: Database record (id, user_id, timestamps)
            - Inner ChatBody: Conversation data (this method builds this)
            - history: Message tree structure
            - models/params: Metadata for reproduction

        Notes:
            - models and params are optional but recommended
            - models list tracks all models used (for multi-model chats)
            - params stores default parameters for consistency

        See Also:
            - build_chat_history(): Builds the history component
            - build_chat_payload(): Wraps this in complete payload
            - create_chat(): Uses this structure
        """
        history = ChatPayloads.build_chat_history(messages, current_id)

        chat_object: ChatBodyDict = {
            "title": title,
            "history": history,
        }

        # Optional fields
        if models:
            chat_object["models"] = models
        if params:
            chat_object["params"] = params

        return chat_object

    @staticmethod
    def build_chat_payload(
        title: str,
        messages: List[MessageDict],
        current_id: MessageID,
        folder_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        models: Optional[List[str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> ChatFormDict:
        """Build complete chat payload for creation/update (top-level ChatForm).

        Constructs the full payload structure required by create_chat() and update_chat().
        This is the highest-level builder that includes all chat components:
        inner chat object, folder assignment, and organizational metadata.

        Official Backend Reference:
            - backend/open_webui/models/chats.py (ChatForm class)
            - backend/open_webui/routers/chats.py:82-135 POST /api/v1/chats/new

        Args:
            title (str): Chat title (displayed in UI)
            messages (List[MessageDict]): Complete message list with tree structure
            current_id (MessageID): Active message ID (defines conversation branch)
            folder_id (Optional[str]): Folder ID for organization
                                      None leaves chat unfoldered
            tags (Optional[List[str]]): Tag names for categorization
                                       Note: Tags handled by backend, not in payload
            models (Optional[List[str]]): Model IDs used
                                         Recommended for reproducibility
            params (Optional[Dict[str, Any]]): Default model parameters
                                              Example: {"temperature": 0.8}

        Returns:
            ChatFormDict: Complete creation payload:
            {
                "chat": {  # Inner chat object
                    "title": str,
                    "history": {...},
                    "models": [...],
                    "params": {...}
                },
                "folder_id": str | None  # Optional folder assignment
            }

        Example:
            ```python
            # Build complete conversation
            user_msg = ChatPayloads.build_user_message(
                "Explain quantum computing",
                model="gpt-4.1"
            )
            asst_msg = ChatPayloads.build_assistant_message(
                "Quantum computing uses quantum mechanics...",
                model="gpt-4.1",
                parent_id=user_msg["id"],
                done=True
            )

            # Build complete payload
            payload = ChatPayloads.build_chat_payload(
                title="Quantum Computing Explained",
                messages=[user_msg, asst_msg],
                current_id=asst_msg["id"],
                folder_id="education-folder-id",
                tags=["physics", "tutorial"],  # Added separately via API
                models=["gpt-4.1"],
                params={"temperature": 0.7, "max_tokens": 1000}
            )

            # Create chat
            chat = chat_api.create_chat(payload)

            # Add tags separately (backend handles this)
            for tag in ["physics", "tutorial"]:
                chat_api.add_chat_tag(chat["id"], tag)
            ```

        Payload Structure Hierarchy:
            ```
            ChatForm (this method builds)
            └─ chat: ChatBody
               ├─ title: str
               ├─ history: ChatHistory
               │  ├─ currentId: str
               │  └─ messages: {id: MessageDict}
               ├─ models: [str]
               └─ params: {}
            └─ folder_id: str | None
            ```

        Tags Handling:
            - tags parameter exists for documentation clarity
            - Tags NOT included in payload (backend limitation)
            - Must add tags separately via add_chat_tag() after creation
            - This is intentional Open WebUI design

        Validation:
            - All validations performed by build_chat_history()
            - Folder must exist before assignment
            - Models list can be empty but recommended

        Use Cases:
            - Create new chat from scratch
            - Update existing chat structure
            - Import/restore chat data
            - Programmatic chat generation

        Notes:
            - This is the standard entry point for chat creation
            - Combines all previous builders into complete payload
            - Ready to pass directly to create_chat()

        See Also:
            - build_chat_object(): Builds inner chat object
            - build_chat_history(): Builds message tree
            - create_chat(): Consumes this payload
            - update_chat(): Also uses this structure
        """
        # Build the inner chat object
        chat_object = ChatPayloads.build_chat_object(
            title=title,
            messages=messages,
            current_id=current_id,
            models=models,
            params=params,
        )

        payload: ChatFormDict = {"chat": chat_object}

        # Add optional fields at top level
        if folder_id:
            payload["folder_id"] = folder_id

        # Meta is stored separately in ChatModel.meta
        # Tags go into meta.tags
        # (handled by backend automatically)

        return payload

    @staticmethod
    def build_completion_payload(
        model: str,
        messages: List[Dict[str, Any]],
        chat_id: Optional[ChatID] = None,
        stream: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        **extra_params: Any,
    ) -> CompletionPayloadDict:
        """
        Build payload for POST /api/chat/completions.

        This is the main completion request format.

        Args:
            model: Model identifier
            messages: Conversation messages (OpenAI-style format)
            chat_id: Optional chat ID for persistence
            stream: Enable streaming response
            metadata: Metadata (chat_id, message_id, etc.)
            **extra_params: Additional parameters (temperature, max_tokens, tools, etc.)

        Official: backend/open_webui/main.py @app.post("/api/chat/completions")
        """
        try:
            # Validate required fields
            if not model or not isinstance(model, str):
                logger.error(f"Invalid model: {model}")
                raise ValueError(
                    f"Model must be a non-empty string, got: {type(model)}"
                )

            if not isinstance(messages, list):
                logger.error(f"Messages must be a list, got: {type(messages)}")
                raise TypeError(f"Messages must be a list, got: {type(messages)}")

            if not messages:
                logger.error("Messages list is empty")
                raise ValueError("Messages list cannot be empty")

            if not isinstance(stream, bool):
                logger.warning(
                    f"Stream should be bool, got {type(stream)}, coercing to bool"
                )
                stream = bool(stream)

            # Validate messages structure
            for idx, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    logger.error(f"Message {idx} is not a dict: {type(msg)}")
                    raise TypeError(f"Message {idx} must be a dict")

                if "role" not in msg or "content" not in msg:
                    logger.error(
                        f"Message {idx} missing required fields (role/content): {msg}"
                    )
                    raise KeyError(f"Message {idx} missing 'role' or 'content' field")

            # Validate optional metadata
            if metadata is not None and not isinstance(metadata, dict):
                logger.error(f"Metadata must be a dict, got: {type(metadata)}")
                raise TypeError(f"Metadata must be a dict, got: {type(metadata)}")

            payload: CompletionPayloadDict = {
                "model": model,
                "messages": messages,
                "stream": stream,
            }

            # Add optional parameters
            if chat_id:
                payload["chat_id"] = chat_id
            if metadata:
                payload["metadata"] = metadata

            # Add any extra parameters (temperature, top_p, tools, etc.)
            for key, value in extra_params.items():
                payload[key] = value  # type: ignore[literal-required]

            return payload

        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Failed to build completion payload: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error building completion payload: {e}", exc_info=True
            )
            raise

    @staticmethod
    def build_completed_payload(
        chat_id: ChatID, message_id: MessageID, **extra_data: Any
    ) -> CompletedPayloadDict:
        """
        Build payload for POST /api/chat/completed.

        Called after completion to finalize state.

        Args:
            chat_id: Chat identifier
            message_id: Message identifier
            **extra_data: Additional completion data

        Official: backend/open_webui/main.py @app.post("/api/chat/completed")

        Note: Backend typically expects 'id' or 'chat_id'. We provide both for safety.
        """
        return {
            "id": chat_id,
            "chat_id": chat_id,
            "message_id": message_id,
            **extra_data,
        }

    @staticmethod
    def convert_to_openai_format(
        messages: List[MessageDict],
    ) -> List[Dict[str, Union[str, List[Dict[str, Any]]]]]:
        """Convert Open WebUI message format to OpenAI API format.

        Extracts only essential fields (role, content) from Open WebUI messages
        for use in completion API calls. Simplifies complex message structures
        while preserving multimodal content blocks.

        This transformation is necessary because:
        - Open WebUI stores rich metadata (parentId, childrenIds, timestamps, etc.)
        - OpenAI API only needs role and content
        - Completion endpoint expects minimal message format

        Args:
            messages (List[MessageDict]): Open WebUI format messages with full structure:
                [
                    {
                        "id": str,
                        "role": str,
                        "content": str | List[ContentBlock],
                        "parentId": str,
                        "childrenIds": [...],
                        "timestamp": int,
                        # ...other fields
                    },
                    ...
                ]

        Returns:
            List[Dict]: OpenAI format messages (minimal structure):
            [
                {
                    "role": "user" | "assistant" | "system",
                    "content": str | List[ContentBlock]
                },
                ...
            ]

        Raises:
            TypeError: If messages not a list or contains non-dict
            KeyError: If message missing "role" field

        Example:
            ```python
            # Get chat messages from Open WebUI
            chat = chat_api.get_chat("chat-123")
            messages = list(chat["chat"]["history"]["messages"].values())

            # Convert to OpenAI format
            openai_messages = ChatPayloads.convert_to_openai_format(messages)

            # Use in completion request
            response = chat_api.completion({
                "model": "gpt-4.1",
                "messages": openai_messages,  # Clean format
                "stream": False
            })

            # Before conversion:
            # {
            #     "id": "msg-123",
            #     "role": "user",
            #     "content": "Hello",
            #     "parentId": None,
            #     "childrenIds": ["msg-456"],
            #     "timestamp": 1704067200
            # }
            #
            # After conversion:
            # {
            #     "role": "user",
            #     "content": "Hello"
            # }
            ```

        Multimodal Content Handling:
            ```python
            # Multimodal messages preserved correctly
            oui_message = {
                "id": "msg-789",
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image_url", "image_url": {"url": "..."}}
                ],
                # ...other fields
            }

            openai_msg = ChatPayloads.convert_to_openai_format([oui_message])[0]
            # Result:
            # {
            #     "role": "user",
            #     "content": [
            #         {"type": "text", "text": "What's in this image?"},
            #         {"type": "image_url", "image_url": {"url": "..."}}
            #     ]
            # }
            # Content blocks preserved for vision models
            ```

        Conversation Path Extraction:
            ```python
            # Extract active conversation path from message tree
            chat = chat_api.get_chat("chat-123")
            history = chat["chat"]["history"]
            current_id = history["currentId"]
            all_messages = history["messages"]

            # Walk back from current to root
            conversation_path = []
            msg_id = current_id
            while msg_id:
                msg = all_messages[msg_id]
                conversation_path.insert(0, msg)  # Prepend for correct order
                msg_id = msg.get("parentId")

            # Convert path to OpenAI format
            openai_messages = ChatPayloads.convert_to_openai_format(
                conversation_path
            )

            # Now ready for completion API
            response = chat_api.completion({
                "model": "gpt-4.1",
                "messages": openai_messages
            })
            ```

        Content Type Handling:
            - String content: Preserved as-is (converted to str)
            - List content (multimodal): Preserved structure
            - Missing content: Uses empty string (with warning)

        Field Extraction:
            - Extracted: role, content
            - Discarded: id, parentId, childrenIds, timestamp, model, files, sources, info, etc.

        Use Cases:
            - Prepare messages for completion API
            - Continue existing conversations
            - Export conversation for external use
            - Message format conversion/migration

        Notes:
            - Lossy conversion: Metadata not recoverable
            - Order matters: Ensure chronological order
            - Missing content field triggers warning
            - Type coercion: Non-string/list content converted to string

        See Also:
            - completion(): Consumes OpenAI format messages
            - build_message(): Creates Open WebUI format
            - build_completion_payload(): Uses OpenAI format
        """
        try:
            if not isinstance(messages, list):
                logger.error(f"Messages must be a list, got: {type(messages)}")
                raise TypeError(f"Messages must be a list, got: {type(messages)}")

            openai_messages = []
            for idx, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    logger.error(f"Message {idx} is not a dict: {type(msg)}")
                    raise TypeError(f"Message {idx} must be a dict")

                if "role" not in msg:
                    logger.error(f"Message {idx} missing 'role' field")
                    raise KeyError(f"Message {idx} missing required 'role' field")

                if "content" not in msg:
                    logger.warning(
                        f"Message {idx} missing 'content' field, using empty string"
                    )
                    content = ""
                else:
                    content = msg["content"]

                # Handle content blocks (multimodal)
                if isinstance(content, list):
                    # Keep content blocks as-is (for images, etc.)
                    openai_messages.append(
                        {"role": msg["role"], "content": content}  # type: ignore[misc]
                    )
                else:
                    # Simple string content
                    openai_messages.append(
                        {
                            "role": msg["role"],
                            "content": str(content),  # type: ignore[misc]
                        }
                    )

            return openai_messages  # type: ignore[return-value]

        except (TypeError, KeyError) as e:
            logger.error(f"Failed to convert to OpenAI format: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error converting to OpenAI format: {e}", exc_info=True
            )
            raise

    @staticmethod
    def add_child_to_parent(
        messages: List[MessageDict], parent_id: MessageID, child_id: MessageID
    ) -> None:
        """Update parent message to include child ID in tree structure.

        Maintains bidirectional message tree relationships by updating
        the parent's childrenIds array. This is essential for supporting
        Open WebUI's branching conversations (edit/regenerate features).

        Tree Structure Maintenance:
        - parentId: Child → Parent link (set when creating child)
        - childrenIds: Parent → Children links (this method updates)
        - Both directions needed for tree traversal

        Args:
            messages (List[MessageDict]): Message list to modify IN PLACE
            parent_id (MessageID): Parent message ID to update
            child_id (MessageID): Child message ID to add to childrenIds

        Returns:
            None: Modifies messages list in place

        Example:
            ```python
            # Linear conversation (one child per parent)
            messages = []

            # Create root message
            user_msg = ChatPayloads.build_user_message("Hello")
            messages.append(user_msg)

            # Create child with parent link
            asst_msg = ChatPayloads.build_assistant_message(
                "Hi there!",
                model="gpt-4.1",
                parent_id=user_msg["id"]  # Child → Parent link
            )
            messages.append(asst_msg)

            # Update parent's childrenIds (Parent → Child link)
            ChatPayloads.add_child_to_parent(
                messages,
                parent_id=user_msg["id"],
                child_id=asst_msg["id"]
            )

            # Now tree is complete:
            # user_msg: {"id": "123", "childrenIds": ["456"], ...}
            # asst_msg: {"id": "456", "parentId": "123", ...}
            ```

        Branching Conversations:
            ```python
            # Create branching (regenerate/edit scenario)
            messages = []

            user_msg = ChatPayloads.build_user_message("Write a poem")
            messages.append(user_msg)

            # First response
            asst_msg_1 = ChatPayloads.build_assistant_message(
                "Roses are red...",
                model="gpt-4.1",
                parent_id=user_msg["id"]
            )
            messages.append(asst_msg_1)
            ChatPayloads.add_child_to_parent(
                messages,
                user_msg["id"],
                asst_msg_1["id"]
            )

            # Alternative response (regenerate)
            asst_msg_2 = ChatPayloads.build_assistant_message(
                "In gardens of dreams...",
                model="gpt-4.1",
                parent_id=user_msg["id"]  # Same parent!
            )
            messages.append(asst_msg_2)
            ChatPayloads.add_child_to_parent(
                messages,
                user_msg["id"],
                asst_msg_2["id"]
            )

            # Result: user_msg has TWO children
            # user_msg: {
            #     "id": "123",
            #     "childrenIds": ["456", "789"],  # Two branches!
            #     ...
            # }
            # UI can switch between branches via currentId
            ```

        In-Place Modification:
            ```python
            # Important: Modifies list in place
            messages = [parent_msg, child_msg]
            print(parent_msg.get("childrenIds"))  # Output: []

            ChatPayloads.add_child_to_parent(
                messages,
                parent_msg["id"],
                child_msg["id"]
            )

            print(parent_msg.get("childrenIds"))  # Output: [child_id]
            # Same object modified, no copy
            ```

        Behavior:
            - Finds parent in list by ID
            - Initializes childrenIds array if not present
            - Appends child_id if not already present
            - Idempotent: Safe to call multiple times with same child_id
            - Silent: No error if parent not found (by design)

        Use Cases:
            - Building conversation trees programmatically
            - Implementing regenerate/edit features
            - Supporting multi-turn branching dialogs
            - Maintaining tree integrity during construction

        Notes:
            - Must call for EACH parent-child relationship
            - Parent must exist in messages list
            - Duplicate children automatically prevented
            - No validation of child existence

        See Also:
            - build_message(): Sets parentId (child → parent)
            - build_chat_history(): Uses complete tree structure
            - Message tree is DAG (directed acyclic graph)
        """
        for msg in messages:
            if msg["id"] == parent_id:
                if "childrenIds" not in msg:
                    msg["childrenIds"] = []
                if child_id not in msg["childrenIds"]:
                    msg["childrenIds"].append(child_id)
                break
