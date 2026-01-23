from typing import Any, Dict, List, Optional, Generator, Union
import logging

from openwebui_chat_client.core.base_manager import BaseManager
from openwebui_chat_client.core.base_client import BaseClient
from openwebui_chat_client.models import ActionResult

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
        self._tasks = ChatTasks(self)
        self._actions = ChatActions(self)

        # Expose properties for internal access if needed (e.g. by ChatTasks)
        self.api = self._api

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
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message using the full 3-step workflow.
        """
        return self._workflow.execute_full_turn(
            question=question,
            chat_id=chat_id,
            model=model or self.base_client.default_model_id,
            chat_title=chat_title,
            auto_title=auto_title,
            auto_followup=auto_followup,
            auto_tags=auto_tags,
            **kwargs,
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
        """
        if not chat_id:
            create_resp = self._api.create_chat(
                {"chat": {"title": chat_title or "New Chat"}}
            )
            if create_resp and "id" in create_resp:
                chat_id = create_resp["id"]
            else:
                return

        model = model or self.base_client.default_model_id

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": question}],
            "stream": True,
            **kwargs,
        }

        stream_resp = self.base_client._stream_request(
            "POST", f"/api/v1/chats/{chat_id}", json_data=payload
        )
        for chunk in stream_resp:
            yield chunk

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
