from typing import Any, Dict, List, Optional, Generator, Union
import logging

from openwebui_chat_client.core.base_manager import BaseManager
from openwebui_chat_client.core.base_client import BaseClient
from openwebui_chat_client.models import ActionResult, ChatResponse, ChatDetails

# Import orchestrated modules
from .api import ChatAPI
from .workflow import ChatWorkflow
from .rag import ChatRAG
from .tasks import ChatTasks
from .actions import ChatActions

logger = logging.getLogger(__name__)


class ChatManager(BaseManager):
    """
    High-Level Chat Manager.

    Exposes public API for chat operations.
    Delegates logic to specialized internal modules.
    Follows strict facade pattern: logic is in sub-modules.
    """

    def __init__(self, base_client: BaseClient):
        super().__init__(base_client)

        # Initialize internal modules
        self._api = ChatAPI(base_client)
        self._workflow = ChatWorkflow(self._api)
        self._rag = ChatRAG()

        # Expose properties for internal access BEFORE initializing dependent modules
        self.api = self._api

        # Initialize modules that depend on exposed properties
        self._tasks = ChatTasks(self)
        self._actions = ChatActions(self)

    # --- Workflow Delegation ---

    def chat(
        self,
        question: str,
        chat_id: Optional[str] = None,
        model: Optional[str] = None,
        chat_title: Optional[str] = None,
        auto_title: bool = True,
        auto_followup: bool = True,
        auto_tags: bool = False,
        **kwargs,
    ) -> Optional[ChatResponse]:
        """
        Send a message using the full 3-step workflow.

        Returns:
            ChatResponse object with response text, chat_id, message_id, etc.
            or None if the operation fails.
        """
        # Find or create the chat context based on priority:
        # 1. chat_id
        # 2. chat_title (search)
        # 3. New nameless chat
        chat_id = self._get_or_create_chat_id(
            chat_id=chat_id or self.base_client.chat_id,
            chat_title=chat_title,
            model=model,
        )
        if not chat_id:
            logger.error("Failed to establish chat context.")
            return None

        # Update client state to maintain chat context
        self.base_client.chat_id = chat_id

        result = self._workflow.execute_full_turn(
            question=question,
            chat_id=chat_id,
            model=model or self.base_client.default_model_id,
            chat_title=None,  # Already handled
            auto_title=auto_title,
            auto_followup=auto_followup,
            auto_tags=auto_tags,
            **kwargs,
        )

        if not result:
            return None

        # Convert workflow result to ChatResponse
        completion_resp = result.get("completion_response", {})
        metadata = result.get("metadata", {})

        # Extract response text from completion
        response_text = None
        if completion_resp:
            choices = completion_resp.get("choices", [])
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                response_text = message.get("content")

        return ChatResponse(
            content=response_text or "",
            chat_id=metadata.get("chat_id", ""),
            message_id=metadata.get("message_id", ""),
            sources=None,
        )

    def stream_chat(
        self,
        question: str,
        chat_id: Optional[str] = None,
        model: Optional[str] = None,
        chat_title: Optional[str] = None,
        **kwargs,
    ) -> Generator[str, None, None]:
        """
        Stream a chat response, yielding plain text strings as they arrive.

        Calls POST /api/chat/completions with stream=True, parses SSE
        (Server-Sent Events) lines and yields the content delta as str.

        Args:
            question:   The user message.
            chat_id:    Existing chat ID (takes priority over chat_title).
            model:      Model override; uses default_model_id if not set.
            chat_title: Title to find-or-create the chat session.

        Yields:
            str: Incremental text content from the model.
        """
        import json as _json

        model = model or self.base_client.default_model_id

        # Find or create the chat context
        chat_id = self._get_or_create_chat_id(
            chat_id=chat_id or self.base_client.chat_id,
            chat_title=chat_title,
            model=model,
        )
        if not chat_id:
            logger.error("Failed to create or find chat context for streaming.")
            return

        self.base_client.chat_id = chat_id

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": question}],
            "stream": True,
            "chat_id": chat_id,
            **{k: v for k, v in kwargs.items() if v is not None},
        }

        stream_bytes = self.base_client._stream_request(
            "POST", "/api/chat/completions", json_data=payload
        )
        if stream_bytes is None:
            return

        for line in stream_bytes:
            # Each line from _stream_request is bytes like b"data: {...}" or b"data: [DONE]"
            if isinstance(line, bytes):
                line = line.decode("utf-8", errors="replace")
            line = line.strip()
            if not line or not line.startswith("data:"):
                continue
            raw = line[len("data:") :].strip()
            if raw == "[DONE]":
                break
            try:
                parsed = _json.loads(raw)
                delta = parsed.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield content
            except (_json.JSONDecodeError, IndexError, KeyError):
                continue

    # --- Regenerate & Edit ---

    def regenerate_message(
        self,
        chat_id: str,
        parent_message_id: str,
        model: Optional[str] = None,
        **kwargs,
    ) -> Optional[ChatResponse]:
        """
        Regenerate the assistant response for a given user message.

        Args:
            chat_id:           The chat containing the message.
            parent_message_id: ID of the user message to regenerate from.
            model:             Model override.

        Returns:
            ChatResponse with the new assistant response, or None on failure.
        """
        result = self._workflow.regenerate_message(
            chat_id=chat_id,
            parent_message_id=parent_message_id,
            model=model or self.base_client.default_model_id,
            **kwargs,
        )
        return self._result_to_response(result)

    def edit_message(
        self,
        chat_id: str,
        message_id: str,
        new_content: str,
        model: Optional[str] = None,
        **kwargs,
    ) -> Optional[ChatResponse]:
        """
        Edit a user message and trigger a new assistant response.

        Args:
            chat_id:     Chat to edit in.
            message_id:  The user message to edit.
            new_content: Replacement text content.
            model:       Model override.

        Returns:
            ChatResponse with the new reply, or None on failure.
        """
        result = self._workflow.edit_message(
            chat_id=chat_id,
            message_id=message_id,
            new_content=new_content,
            model=model or self.base_client.default_model_id,
            **kwargs,
        )
        return self._result_to_response(result)

    def _result_to_response(self, result: Optional[dict]) -> Optional[ChatResponse]:
        """Convert a WorkflowResultDict to a ChatResponse object."""
        if not result:
            return None
        completion_resp = result.get("completion_response", {})
        metadata = result.get("metadata", {})
        response_text = None
        if completion_resp:
            choices = completion_resp.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                response_text = message.get("content")
        return ChatResponse(
            content=response_text or "",
            chat_id=metadata.get("chat_id", ""),
            message_id=metadata.get("message_id", ""),
            sources=None,
        )

    # --- Task Processing Delegation ---

    def process_task(
        self,
        question: str,
        model_id: str,
        tool_server_ids: Union[str, List[str]],
        knowledge_base_name: Optional[str] = None,
        max_iterations: int = 25,
        summarize_history: bool = False,
        decision_model_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Process a task (ReAct loop).Delegate to ChatTasks."""
        return self._tasks.process_task(
            question=question,
            model_id=model_id,
            tool_server_ids=tool_server_ids,
            knowledge_base_name=knowledge_base_name,
            max_iterations=max_iterations,
            summarize_history=summarize_history,
            decision_model_id=decision_model_id,
        )

    def _perform_research_step(
        self,
        topic: str,
        chat_title: str,
        research_history: List[str],
        step_num: int,
        total_steps: int,
        general_models: List[str],
        search_models: List[str],
    ) -> Optional[tuple]:
        """Deep research step delegation. Required by OpenWebUIClient."""
        return self._tasks._perform_research_step(
            topic=topic,
            chat_title=chat_title,
            research_history=research_history,
            step_num=step_num,
            total_steps=total_steps,
            general_models=general_models,
            search_models=search_models,
        )

    # --- Action Delegation ---

    def trigger_action(
        self,
        action_id: str,
        chat_id: str,
        message_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[ActionResult]:
        """Trigger an action. Delegate to ChatActions."""
        return self._actions.trigger_action(
            action_id=action_id, chat_id=chat_id, message_id=message_id, params=params
        )

    # --- API Delegation (Read Operations) ---

    def list_chats(
        self,
        page: int = 1,
        include_pinned: bool = False,
        include_folders: bool = False,
        **kwargs,
    ) -> List[ChatDetails]:
        """List chats."""
        chats = self._api.list_chats(
            page=page,
            include_pinned=include_pinned,
            include_folders=include_folders,
            **kwargs,
        )
        return [ChatDetails.model_validate(c) for c in chats] if chats else []

    def get_chat(self, chat_id: str) -> Optional[ChatDetails]:
        """Get chat details."""
        chat = self._api.get_chat(chat_id)
        return ChatDetails.model_validate(chat) if chat else None

    def search_chats(self, query: str, page: int = 1) -> List[ChatDetails]:
        """Search chats."""
        chats = self._api.search_chats(query, page)
        return [ChatDetails.model_validate(c) for c in chats] if chats else []

    # --- API Delegation (Write Operations) ---

    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat."""
        return self._api.delete_chat(chat_id)

    def delete_all_chats(self) -> bool:
        """Delete all chats."""
        return self._api.delete_all_chats()

    def rename_chat(self, chat_id: str, new_title: str) -> bool:
        """Rename a chat."""
        return self._api.rename_chat(chat_id, new_title)

    def set_chat_tags(self, chat_id: str, tags: List[str]) -> bool:
        """Set tags for a chat."""
        return self._api.set_chat_tags(chat_id, tags)

    def set_chat_folder(self, chat_id: str, folder_id: str) -> bool:
        """Move chat to a folder."""
        return self._api.set_chat_folder(chat_id, folder_id)

    def archive_chat(self, chat_id: str, archive: bool = True) -> bool:
        """Archive or unarchive a chat."""
        return self._api.archive_chat(chat_id, archive)

    def _get_or_create_chat_id(
        self,
        chat_id: Optional[str] = None,
        chat_title: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Optional[str]:
        """
        Helper to establish chat ID according to priority:
        1. chat_id (if provided, use it directly)
        2. chat_title (search for existing chat by title)
        3. Create new nameless chat
        """
        if chat_id:
            return chat_id

        if chat_title:
            # Search for existing chat by title
            logger.info(f"Searching for existing chat with title: '{chat_title}'")
            found = self.search_chats(chat_title)
            if found:
                for c in found:
                    if c.get("title") == chat_title:
                        cid = c.get("id")
                        logger.info(f"Found existing chat: {chat_title} ({cid})")
                        return cid

        # Create new chat
        model_id = model or self.base_client.default_model_id
        title = chat_title or "New Chat"
        logger.info(f"Creating new chat: '{title}'")

        from .payloads import ChatPayloads

        payload = ChatPayloads.build_chat_payload(
            title=title,
            messages=[],
            current_id="",
            models=[model_id] if model_id else [],
        )

        resp = self._api.create_chat(payload)
        if resp:
            cid = (
                resp.get("id") if isinstance(resp, dict) else getattr(resp, "id", None)
            )
            if cid:
                logger.info(f"Successfully created chat: {cid}")
                return cid

        return None

    def switch_chat_model(self, chat_id: str, new_model_id: str) -> bool:
        """
        Switch the model for an existing chat.

        Args:
            chat_id: Chat ID to update
            new_model_id: New model ID to switch to

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current chat state
            chat = self._api.get_chat(chat_id)
            if not chat:
                logger.error(f"Chat {chat_id} not found")
                return False

            # Update the model in the chat object
            chat_inner = chat.get("chat", {})
            current_models = chat_inner.get("models", [])

            # Replace or add the new model
            if not current_models:
                new_models = [new_model_id]
            else:
                new_models = [new_model_id]

            chat_inner["models"] = new_models

            # Update the chat
            update_payload = {"chat": chat_inner}
            result = self._api.update_chat(chat_id, update_payload)

            if result:
                logger.info(
                    f"Successfully switched chat {chat_id} to model {new_model_id}"
                )
                return True
            else:
                logger.error(f"Failed to update chat {chat_id} with new model")
                return False
        except Exception as e:
            logger.error(
                f"Error switching model for chat {chat_id}: {e}", exc_info=True
            )
            return False

    # --- Folder & Metadata Operations ---

    def create_folder(self, name: str) -> Optional[str]:
        """Create a folder and return ID."""
        resp = self._api.create_folder(name)
        if resp and "id" in resp:
            return resp["id"]
        return None

    def get_folder_id_by_name(self, name: str) -> Optional[str]:
        """Get folder ID by name."""
        folders = self._api.list_folders()
        for f in folders:
            if f.get("name") == name:
                return f.get("id")
        return None

    def update_chat_metadata(
        self,
        chat_id: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_name: Optional[str] = None,
    ) -> bool:
        """Update multiple metadata fields."""
        success = True
        if title:
            if not self.rename_chat(chat_id, title):
                success = False
        if tags:
            if not self.set_chat_tags(chat_id, tags):
                success = False
        if folder_name:
            fid = self.get_folder_id_by_name(folder_name)
            if not fid:
                fid = self.create_folder(folder_name)
            if fid:
                if not self.set_chat_folder(chat_id, fid):
                    success = False
            else:
                success = False
        return success

    # --- RAG / File Operations ---

    def upload_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Upload a file for RAG."""
        return self._api.upload_file(file_path)

    # --- Internal Helpers ---

    def _find_or_create_chat_by_title(self, title: str) -> str:
        """Helper for tasks to ensure a chat exists."""
        chat_id = self._get_or_create_chat_id(chat_title=title)
        if chat_id:
            self.base_client.chat_id = chat_id
            return chat_id
        return ""

    # --- Parallel Chat ---

    def parallel_chat(self, question: str, model_ids: List[str], **kwargs) -> Optional['ParallelChatResponse']:
        """
        Execute parallel chat with multiple models.
        Load module lazily to avoid circular imports if any.
        """
        if not model_ids:
            return None

        from .parallel import ChatParallel
        from .payloads import ChatPayloads
        from openwebui_chat_client.models import ParallelChatResponse, ChatResponse

        parallel = ChatParallel(self._api)
        user_message = ChatPayloads.build_user_message(question)
        
        # Avoid duplicate chat_id in kwargs
        chat_id = kwargs.pop("chat_id", None)
        
        raw_results = parallel.run_parallel(
            chat_id=chat_id,
            user_message=user_message,
            model_ids=model_ids,
            **kwargs
        )

        if not raw_results:
            return None

        # Format into ParallelChatResponse
        responses = {}
        message_ids = {}
        final_chat_id = chat_id

        for res in raw_results:
            model_id = res["model"]
            api_resp = res["response"]
            
            # Extract content from OpenAI-style response
            content = ""
            if api_resp.get("choices"):
                content = api_resp["choices"][0].get("message", {}).get("content", "")
            
            msg_id = api_resp.get("id", "")
            
            responses[model_id] = ChatResponse(
                content=content,
                chat_id=final_chat_id or "",
                message_id=msg_id
            )
            message_ids[model_id] = msg_id

        return ParallelChatResponse(
            responses=responses,
            chat_id=final_chat_id or "",
            message_ids=message_ids
        )
