"""
Chat Workflow Orchestrator - Official Open WebUI Flow Implementation.

This module implements the complete Open WebUI chat workflow, strictly following
the official backend implementation in backend/open_webui/main.py and utils/middleware.py.

Official Flow Reference:
    1. POST /api/chat/completions - Generate response with metadata
    2. POST /api/chat/completed - Apply outlet filters (background tasks)
    3. POST /api/v1/chats/new or /{id} - Persist chat state

Key Concepts:
    - Metadata propagation: chat_id, message_id, parent_message_id, session_id
    - Content blocks: [{type: "text|tool_calls|reasoning", content: ...}]
    - Event-driven streaming: Socket.IO events for real-time updates
    - Background tasks: Follow-ups, tags, image generation after completion

Official Backend Sources:
    - backend/open_webui/main.py:1565-1857 (chat_completion endpoint)
    - backend/open_webui/utils/middleware.py:952-3713 (process_chat_payload/response)
    - backend/open_webui/utils/chat.py:170-363 (generate_chat_completion)
"""

from typing import Any, Dict, List, Optional, Generator
import logging
import time
import json

# Local imports
from .api import ChatAPI
from .payloads import ChatPayloads
from .rag import ChatRAG
from .parallel import ChatParallel

# Type definitions
from .types import (
    MessageDict,
    ChatDict,
    ResponseDict,
    WorkflowResultDict,
    MetadataDict,
    ChatID,
    MessageID,
    SessionID,
)

logger = logging.getLogger(__name__)


class ChatWorkflow:
    """
    Chat Workflow Orchestrator.

    Implements the complete 3-step Open WebUI chat workflow:
    1. Completion: Generate response with metadata tracking
    2. Completed: Apply outlet filters and background tasks
    3. Persist: Save final chat state to database

    This orchestrator coordinates between API calls, payload construction,
    and state management to ensure full compatibility with Open WebUI backend.

    Official Backend Reference:
        - backend/open_webui/main.py:chat_completion() (lines 1565-1857)
        - backend/open_webui/utils/middleware.py:process_chat_payload/response
    """

    def __init__(self, chat_api: ChatAPI):
        """
        Initialize workflow orchestrator.

        Args:
            chat_api: ChatAPI instance for HTTP requests
        """
        self.api = chat_api
        self.parallel = ChatParallel(chat_api)

    def execute_full_turn(
        self,
        question: str,
        chat_id: Optional[ChatID] = None,
        model: Optional[str] = None,
        chat_title: Optional[str] = None,
        parent_message_id: Optional[MessageID] = None,
        session_id: Optional[SessionID] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        tool_ids: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Optional[WorkflowResultDict]:
        """
        Execute complete chat turn following official Open WebUI workflow.

        Official Backend Flow:
            Step 1: POST /api/chat/completions
                - Validate metadata (chat_id, message_id, parent_message_id)
                - Process chat payload (RAG, tools, files, memory)
                - Generate completion via model provider
                - Stream or return full response

            Step 2: POST /api/chat/completed (automatic via frontend)
                - Apply outlet filters
                - Run background tasks (follow-ups, tags, image gen)
                - Update message metadata

            Step 3: POST /api/v1/chats/{id} (automatic via frontend)
                - Persist final chat state
                - Update history.currentId
                - Save message tree structure

        Args:
            question: User's question/prompt
            chat_id: Existing chat ID or None for new chat
            model: Model ID (e.g., "gpt-4.1", "gemini-2.5-flash")
            parent_message_id: Parent message ID for branching
            session_id: WebSocket session ID for streaming
            files: List of file attachments (multimodal)
            tool_ids: List of tool IDs to enable
            stream: Enable streaming response
            **kwargs: Additional parameters (filter_ids, features, variables, etc.)

        Returns:
            Complete chat response with:
                - response: API completion response
                - chat_state: Final persisted chat state
                - metadata: Tracking info (chat_id, message_id, etc.)
            Returns None if any step fails.

        Official Backend Reference:
            - backend/open_webui/main.py:1565-1857 (chat_completion)
            - backend/open_webui/utils/middleware.py:1402-1909 (process_chat_payload)
            - backend/open_webui/utils/middleware.py:1909-3713 (process_chat_response)
        """
        workflow_step = "initialization"

        try:
            # --- Step 0: Metadata Preparation ---
            workflow_step = "metadata_preparation"
            logger.info("Starting workflow - Step 0: Metadata Preparation")

            # Validate inputs
            if not question or not isinstance(question, str):
                logger.error(f"Invalid question: {question}")
                return None

            if not model or not isinstance(model, str):
                logger.error(f"Invalid model: {model}")
                return None

            # Official metadata structure from backend/open_webui/main.py:1638-1674
            if not chat_id:
                try:
                    # Create new chat
                    title = chat_title or kwargs.get("title", "New Chat")
                    chat_payload = ChatPayloads.build_chat_payload(
                        title=title,
                        messages=[],
                        current_id="",
                        models=[model] if model else [],
                        folder_id=kwargs.get("folder_id"),
                    )
                    chat_resp = self.api.create_chat(chat_payload)
                    if not chat_resp:
                        logger.error("Failed to create new chat")
                        return None
                    chat_id = chat_resp.get("id")
                    logger.info(f"Created new chat: {chat_id}")
                except Exception as e:
                    logger.error(f"Chat creation failed: {e}", exc_info=True)
                    return None

            # Build user message with official structure
            try:
                user_msg = ChatPayloads.build_user_message(
                    content=question,
                    model=model,
                    parent_id=parent_message_id,
                    files=files,
                )
                user_message_id = user_msg["id"]
            except Exception as e:
                logger.error(f"Failed to build user message: {e}", exc_info=True)
                return None

            # Construct metadata (official structure from main.py:1638-1674)
            metadata = {
                "chat_id": chat_id,
                "message_id": user_message_id,
                "parent_message_id": parent_message_id,
                "session_id": session_id or f"session_{int(time.time())}",
                "filter_ids": kwargs.get("filter_ids", []),
                "tool_ids": tool_ids or kwargs.get("tool_ids"),
                "files": files,
                "features": kwargs.get("features", {}),
                "variables": kwargs.get("variables", {}),
            }

            # --- Step 1: Completion Request ---
            workflow_step = "completion"
            logger.info(
                f"Executing workflow - Step 1: Completion (chat_id={chat_id}, model={model})"
            )

            try:
                completion_payload = ChatPayloads.build_completion_payload(
                    model=model,
                    messages=[user_msg],
                    chat_id=chat_id,
                    message_id=user_message_id,
                    parent_message_id=parent_message_id,
                    session_id=metadata["session_id"],
                    stream=stream,
                    files=files,
                    tool_ids=tool_ids,
                    **kwargs,
                )
            except Exception as e:
                logger.error(f"Failed to build completion payload: {e}", exc_info=True)
                return None

            # Send completion request
            completion_resp = self.api.completion(completion_payload)
            if not completion_resp:
                logger.error("Completion request failed")
                return None

            # Extract assistant message from response
            try:
                if stream:
                    # For streaming, would need to collect chunks
                    logger.warning("Streaming not fully implemented in this example")
                    assistant_content = "Streaming response"
                    assistant_message_id = f"msg_{int(time.time())}"
                else:
                    # Extract content from OpenAI-format response
                    choices = completion_resp.get("choices", [])

                    if not choices and "task_id" in completion_resp:
                        # Handle background task polling (discovered via browser)
                        task_id = completion_resp["task_id"]
                        logger.info(
                            f"Completion returned task_id={task_id}, polling for completion..."
                        )
                        assistant_content = self._poll_chat_for_completion(
                            chat_id, user_message_id
                        )
                        if assistant_content is None:
                            logger.error(
                                "Failed to retrieve completed message via polling"
                            )
                            return None
                        assistant_message_id = f"msg_{int(time.time())}"  # We might need to extract the real one if needed
                    elif not choices:
                        logger.error("No choices in completion response")
                        return None
                    else:
                        assistant_message = choices[0].get("message", {})
                        assistant_content = assistant_message.get("content", "")
                        assistant_message_id = completion_resp.get(
                            "id", f"msg_{int(time.time())}"
                        )

                    # Update metadata with assistant message ID
                    metadata["message_id"] = assistant_message_id

                logger.info(
                    f"Completion successful: message_id={metadata['message_id']}"
                )
            except KeyError as e:
                logger.error(f"Missing key in completion response: {e}", exc_info=True)
                return None
            except Exception as e:
                logger.error(f"Failed to parse completion response: {e}", exc_info=True)
                return None

            # --- Step 2: Completed (Outlet Filters) ---
            workflow_step = "completed"
            logger.info("Executing workflow - Step 2: Completed (outlet filters)")

            completed_resp = None
            try:
                completed_payload = ChatPayloads.build_completed_payload(
                    chat_id=chat_id,
                    message_id=metadata["message_id"],
                    model=model,
                    messages=[user_msg],
                    session_id=metadata["session_id"],
                    **kwargs,
                )

                completed_resp = self.api.completed(completed_payload)
                if not completed_resp:
                    # Non-fatal: completed is optional
                    logger.warning(
                        "Completed request failed (non-fatal, continuing workflow)"
                    )
                else:
                    logger.info("Completed processing successful")
            except Exception as e:
                # Non-fatal: completed step failure shouldn't stop workflow
                logger.warning(f"Completed step failed (non-fatal): {e}")

            # --- Step 3: Persist Chat State ---
            workflow_step = "persist"
            logger.info(
                f"Executing workflow - Step 3: Persist chat state (chat_id={chat_id})"
            )

            # Get existing history to avoid overwriting/wiping messages
            all_messages = self._get_existing_messages(chat_id)

            # Filter out any old versions of the new messages (shouldn't happen but safe)
            new_ids = {user_msg["id"], assistant_message_id}
            all_messages = [
                m
                for m in all_messages
                if (m.get("id") if hasattr(m, "get") else getattr(m, "id", None))
                not in new_ids
            ]

            final_state = None
            max_persist_retries = 2

            for persist_attempt in range(max_persist_retries):
                try:
                    # Build assistant message with official structure
                    assistant_msg = ChatPayloads.build_assistant_message(
                        content=assistant_content,
                        model=model,
                        parent_id=user_message_id,
                        msg_id=metadata["message_id"],
                        done=True,
                    )

                    # Build combined messages list
                    current_messages = all_messages + [user_msg, assistant_msg]

                    # Update chat with complete history
                    chat_object = ChatPayloads.build_chat_object(
                        title=chat_title or kwargs.get("title", "New Chat"),
                        messages=current_messages,
                        current_id=assistant_msg["id"],
                        models=[model] if model else [],
                    )

                    persist_payload = {
                        "chat": chat_object,
                        "folder_id": kwargs.get("folder_id"),
                    }

                    final_state = self.api.update_chat(chat_id, persist_payload)
                    if final_state:
                        logger.info(f"Chat state persisted successfully: {chat_id}")
                        break
                    else:
                        logger.warning(
                            f"Persist attempt {persist_attempt + 1}/{max_persist_retries} failed"
                        )
                        if persist_attempt < max_persist_retries - 1:
                            time.sleep(0.5)

                except Exception as e:
                    logger.error(
                        f"Persist attempt {persist_attempt + 1}/{max_persist_retries} error: {e}",
                        exc_info=True,
                    )
                    if persist_attempt < max_persist_retries - 1:
                        time.sleep(0.5)

            if not final_state:
                logger.error(
                    f"Failed to persist chat state after {max_persist_retries} attempts"
                )
                # Return partial result even if persist failed
                return {
                    "success": False,
                    "chat_id": chat_id,
                    "metadata": metadata,
                    "completion_response": completion_resp,
                    "error": "Failed to persist chat state",
                    "workflow_step_failed": "persist",
                }

            # --- Return Complete Result ---
            return {
                "success": True,
                "chat_id": chat_id,
                "metadata": metadata,
                "user_message": user_msg,
                "assistant_message": {
                    "id": metadata["message_id"],
                    "content": assistant_content,
                },
                "completion_response": completion_resp,
                "completed_response": completed_resp,
                "chat_state": final_state,
            }

        except Exception as e:
            logger.error(
                f"Workflow execution failed at step '{workflow_step}': {e}",
                exc_info=True,
            )
            return {
                "success": False,
                "error": str(e),
                "workflow_step_failed": workflow_step,
                "chat_id": chat_id if "chat_id" in locals() else None,
            }

    def _get_existing_messages(self, chat_id: Optional[ChatID]) -> List[MessageDict]:
        """Helper to fetch and extract all existing messages from a chat."""
        if not chat_id:
            return []

        details = self.api.get_chat(chat_id)
        if not details:
            return []

        chat_data = (
            details.get("chat", {})
            if hasattr(details, "get")
            else getattr(details, "chat", {})
        )
        history = (
            chat_data.get("history", {})
            if hasattr(chat_data, "get")
            else getattr(chat_data, "history", {})
        )
        messages_dict = (
            history.get("messages", {})
            if hasattr(history, "get")
            else getattr(history, "messages", {})
        )

        if hasattr(messages_dict, "values"):
            return list(messages_dict.values())
        return []

    def regenerate_message(
        self,
        chat_id: ChatID,
        parent_message_id: MessageID,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Regenerate the assistant reply for an existing user message.

        Fetches the current chat history, finds the user message identified by
        parent_message_id, and calls execute_full_turn with that message content,
        producing a fresh assistant response as a new branch.

        Args:
            chat_id:           The chat to regenerate in.
            parent_message_id: The user message whose reply should be regenerated.
            model:             Model override.

        Returns:
            WorkflowResultDict with the new assistant response, or None on failure.
        """
        # Fetch existing chat to find the user message content
        details = self.api.get_chat(chat_id)
        if not details:
            logger.error(f"regenerate_message: cannot fetch chat {chat_id}")
            return None

        chat_data = (
            details.get("chat", {})
            if hasattr(details, "get")
            else getattr(details, "chat", {})
        )
        history = (
            chat_data.get("history", {})
            if hasattr(chat_data, "get")
            else getattr(chat_data, "history", {})
        )
        messages = (
            history.get("messages", {})
            if hasattr(history, "get")
            else getattr(history, "messages", {})
        )

        parent_msg = (
            messages.get(parent_message_id) if hasattr(messages, "get") else None
        )
        if parent_msg is None:
            available_keys = (
                list(messages.keys()) if hasattr(messages, "keys") else "unknown"
            )
            logger.error(
                f"regenerate_message: message {parent_message_id} not found. "
                f"Available messages: {available_keys}"
            )
            return None

        content = (
            parent_msg.get("content")
            if isinstance(parent_msg, dict)
            else getattr(parent_msg, "content", None)
        )
        if not content:
            logger.error(
                f"regenerate_message: no content in message {parent_message_id}"
            )
            return None

        # Find parent of the user message (grandparent) to set as new parent
        grandparent_id = (
            parent_msg.get("parentId")
            if isinstance(parent_msg, dict)
            else getattr(parent_msg, "parentId", None)
        )

        return self.execute_full_turn(
            question=content,
            chat_id=chat_id,
            model=model,
            parent_message_id=grandparent_id,
            **kwargs,
        )

    def edit_message(
        self,
        chat_id: ChatID,
        message_id: MessageID,
        new_content: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Edit a user message and trigger a new assistant response.

        Sends the edited content as a new user turn on the same chat (as a branch
        from the edited message's parent), effectively replacing the conversation
        from that point forward.

        Args:
            chat_id:     Chat to edit in.
            message_id:  The user message to edit.
            new_content: New text for the user message.
            model:       Model override.

        Returns:
            WorkflowResultDict with the new assistant response, or None on failure.
        """
        # Fetch existing chat to find the message's parent
        details = self.api.get_chat(chat_id)
        if not details:
            logger.error(f"edit_message: cannot fetch chat {chat_id}")
            return None

        chat_data = chat_data = (
            details.get("chat", {})
            if hasattr(details, "get")
            else getattr(details, "chat", {})
        )
        history = (
            chat_data.get("history", {})
            if hasattr(chat_data, "get")
            else getattr(chat_data, "history", {})
        )
        messages = (
            history.get("messages", {})
            if hasattr(history, "get")
            else getattr(history, "messages", {})
        )

        target_msg = messages.get(message_id) if hasattr(messages, "get") else None
        if target_msg is None:
            available_keys = (
                list(messages.keys()) if hasattr(messages, "keys") else "unknown"
            )
            logger.error(
                f"edit_message: message {message_id} not found. "
                f"Available messages: {available_keys}"
            )
            return None

        # Use the original message's parent as new parent so the edit is a proper branch
        parent_id = (
            target_msg.get("parentId")
            if isinstance(target_msg, dict)
            else getattr(target_msg, "parentId", None)
        )

        return self.execute_full_turn(
            question=new_content,
            chat_id=chat_id,
            model=model,
            parent_message_id=parent_id,
            **kwargs,
        )

    def execute_streaming_turn(
        self,
        question: str,
        chat_id: Optional[ChatID] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Generator[Dict[str, Any], None, None]]:
        """
        Execute streaming chat turn with real-time updates.

        This is a more complex flow that requires WebSocket/SSE handling.
        The official backend uses Socket.IO for event streaming.

        Official Backend Reference:
            - backend/open_webui/utils/middleware.py:2297-3713 (process_chat_response streaming)
            - backend/open_webui/socket/main.py (Socket.IO event handling)

        Args:
            question: User's question
            chat_id: Chat ID
            model: Model ID
            **kwargs: Additional parameters

        Yields:
            Stream of events:
                - {"type": "status", "data": {...}}
                - {"type": "chat:completion", "data": {...}}
                - {"type": "chat:completion", "data": {"done": True}}

        Returns:
            Generator of streaming events, or None if setup fails.
        """
        # Note: Streaming requires WebSocket/SSE integration
        # This is a placeholder for the streaming implementation
        logger.warning("Streaming workflow not fully implemented")

        # Would need to:
        # 1. Establish WebSocket connection with session_id
        # 2. Send completion request with stream=True
        # 3. Listen for Socket.IO events
        # 4. Yield parsed events to caller
        # 5. Handle completion and persist at stream end

        return None

    def _init_new_chat(self, title: str, **kwargs: Any) -> Optional[ChatID]:
        """
        Create a new chat session.

        Args:
            title: Chat title
            **kwargs: Additional chat parameters (folder_id, meta, etc.)

        Returns:
            Chat ID or None if creation fails.

        Official Backend Reference:
            - backend/open_webui/routers/chats.py:create_new_chat()
        """
        chat_payload = ChatPayloads.build_chat_payload(
            title=title,
            messages=[],
            current_id=None,
            folder_id=kwargs.get("folder_id"),
            meta=kwargs.get("meta"),
        )

        resp = self.api.create_chat(chat_payload)
        if not resp:
            logger.error(f"Failed to create chat: {title}")
            return None

        chat_id = resp.get("id")
        logger.info(f"Created chat: {chat_id} (title: {title})")
        return chat_id
