from typing import Any, Dict, List, Optional, Generator, Union
import logging

from openwebui_chat_client.core.base_manager import BaseManager
from openwebui_chat_client.core.base_client import BaseClient
from openwebui_chat_client.models import ActionResult, ChatResponse

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
        result = self._workflow.execute_full_turn(
            question=question,
            chat_id=chat_id,
            model=model or self.base_client.default_model_id,
            chat_title=chat_title,
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
            response=response_text,
            chat_id=metadata.get("chat_id"),
            message_id=metadata.get("message_id"),
            suggested_tags=None,  # TODO: Extract from result if available
            suggested_title=None,  # TODO: Extract from result if available
            follow_ups=None,  # TODO: Extract from result if available
            sources=None,
        )

    def stream_chat(
        self,
        question: str,
        chat_id: Optional[str] = None,
        model: Optional[str] = None,
        chat_title: Optional[str] = None,
        **kwargs,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a chat response.
        
        Yields:
            Dictionaries containing streaming chunks of the response.
        """
        import json
        import uuid
        
        if not chat_id:
            create_resp = self._api.create_chat(
                {"chat": {"title": chat_title or "New Chat"}}
            )
            if create_resp and "id" in create_resp:
                chat_id = create_resp["id"]
            else:
                return

        model = model or self.base_client.default_model_id

        # Build streaming completion payload
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": question}],
            "stream": True,
            "session_id": str(uuid.uuid4()),
            **kwargs,
        }

        stream_resp = self._api.stream_completion(payload)
        if not stream_resp:
            return
        
        for chunk in stream_resp:
            if chunk.startswith(b'data: '):
                data_str = chunk[6:].decode('utf-8').strip()
                if data_str == '[DONE]':
                    break

                try:
                    data = json.loads(data_str)
                    yield data
                except json.JSONDecodeError:
                    continue

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
    ) -> List[Dict[str, Any]]:
        """List chats."""
        return self._api.list_chats(
            page=page,
            include_pinned=include_pinned,
            include_folders=include_folders,
            **kwargs,
        )

    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat details."""
        return self._api.get_chat(chat_id)

    def search_chats(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search chats."""
        return self._api.search_chats(query, page)

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
                logger.info(f"Successfully switched chat {chat_id} to model {new_model_id}")
                return True
            else:
                logger.error(f"Failed to update chat {chat_id} with new model")
                return False
        except Exception as e:
            logger.error(f"Error switching model for chat {chat_id}: {e}", exc_info=True)
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
        # Check current chat status from base_client
        if self.base_client.chat_id:
            return self.base_client.chat_id

        # Try to find by title or create
        # Simplified: just create or use existing
        # But this method was expected by ChatTasks.
        # Implem:
        self.base_client.chat_id = None  # Reset

        # Search for existing (Optional logic)
        found = self.search_chats(title)
        if found:
            # Pick first?
            # Ideally verify title match
            for c in found:
                if c.get("title") == title:
                    self.base_client.chat_id = c["id"]
                    return c["id"]

        # Create
        resp = self._api.create_chat({"chat": {"title": title}})
        if resp and "id" in resp:
            self.base_client.chat_id = resp["id"]
            return resp["id"]
        return ""

    # --- Parallel Chat ---

    def parallel_chat(self, question: str, model_ids: List[str], **kwargs) -> Any:
        """
        Execute parallel chat with multiple models.
        Load module lazily to avoid circular imports if any.
        """
        from .parallel import ChatParallel

        parallel = ChatParallel(self._api, self._workflow)
        return parallel.parallel_chat(question, model_ids, **kwargs)
