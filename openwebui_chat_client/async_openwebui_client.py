"""
Async OpenWebUI Client - Async version of the client.
"""

import logging
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, List, Optional

from openwebui_chat_client.models import (
    ActionResult,
    ChatDetails,
    ChatResponse,
    Function,
)

if TYPE_CHECKING:
    pass

from .core.async_base_client import AsyncBaseClient

from .modules.async_ import (
    AsyncChatManager,
    AsyncFileManager,
    AsyncKnowledgeBaseManager,
    AsyncModelManager,
    AsyncNotesManager,
    AsyncPromptsManager,
    AsyncUserManager,
    AsyncFunctionsManager,
    AsyncToolsManager,
)

logger = logging.getLogger(__name__)


class AsyncOpenWebUIClient:
    """
    Asynchronous Python client for the Open WebUI API.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        default_model_id: str,
        timeout: float = 60.0,
        **kwargs,
    ):
        self._base_client = AsyncBaseClient(
            base_url, token, default_model_id, timeout, **kwargs
        )
        self._base_client._parent_client = self

        self._chat_manager = AsyncChatManager(self._base_client)
        self._model_manager = AsyncModelManager(self._base_client)
        self._user_manager = AsyncUserManager(self._base_client)
        self._file_manager = AsyncFileManager(self._base_client)
        self._kb_manager = AsyncKnowledgeBaseManager(self._base_client)
        self._prompts_manager = AsyncPromptsManager(self._base_client)
        self._notes_manager = AsyncNotesManager(self._base_client)
        self._functions_manager = AsyncFunctionsManager(self._base_client)
        self._tools_manager = AsyncToolsManager(self._base_client)

    async def close(self):
        """Close the client."""
        await self._base_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    # Chat
    async def chat(
        self,
        question: str,
        chat_id: Optional[str] = None,
        chat_title: Optional[str] = None,
        model_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[ChatResponse]:
        response = await self._chat_manager.chat(
            question=question,
            chat_id=chat_id or self._base_client.chat_id,
            chat_title=chat_title,
            model_id=model_id,
            **kwargs,
        )
        if response and response.chat_id:
            self._base_client.chat_id = response.chat_id
        return response

    async def trigger_action(
        self,
        action_id: str,
        chat_id: str,
        message_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[ActionResult]:
        """
        Trigger a specific action for a chat message asynchronously.

        Args:
            action_id: The ID of the action to trigger (e.g., "异步上下文压缩")
            chat_id: The ID of the chat containing the message
            message_id: The ID of the message to apply the action to
            params: Optional dictionary of additional parameters for the action

        Returns:
            The response from the action (usually a dictionary), or None if failed.
        """
        return await self._chat_manager.trigger_action(
            action_id, chat_id, message_id, params
        )

    async def stream_chat(
        self,
        question: str,
        chat_id: Optional[str] = None,
        chat_title: Optional[str] = None,
        model_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        async for chunk in self._chat_manager.stream_chat(
            question=question,
            chat_id=chat_id,
            chat_title=chat_title,
            model_id=model_id,
            **kwargs,
        ):
            yield chunk

    async def get_functions(self) -> Optional[List[Function]]:
        """
        Get all available functions (actions/tools).

        Returns:
            List of function definitions or None if failed
        """
        return await self._chat_manager.get_functions()

    async def get_chat(self, chat_id: str) -> Optional[ChatDetails]:
        """
        Get full details of a specific chat.

        Args:
            chat_id: The ID of the chat to retrieve

        Returns:
            ChatDetails object containing chat details or None if failed
        """
        return await self._chat_manager.get_chat(chat_id)

    async def list_chats(
        self, page: Optional[int] = None
    ) -> Optional[List[ChatDetails]]:
        return await self._chat_manager.list_chats(page)

    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat asynchronously."""
        return await self._chat_manager.delete_chat(chat_id)

    async def regenerate_message(
        self,
        chat_id: str,
        parent_message_id: str,
        model_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[ChatResponse]:
        """Regenerate assistant response asynchronously."""
        return await self._chat_manager.regenerate_message(
            chat_id, parent_message_id, model_id, **kwargs
        )

    async def edit_message(
        self,
        chat_id: str,
        message_id: str,
        new_content: str,
        model_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[ChatResponse]:
        """Edit a user message and trigger new branch asynchronously."""
        return await self._chat_manager.edit_message(
            chat_id, message_id, new_content, model_id, **kwargs
        )

    async def search_chats(
        self, query: str, page: Optional[int] = None
    ) -> Optional[List[ChatDetails]]:
        """Search chats by text query asynchronously."""
        return await self._chat_manager.search_chats(query, page)

    async def list_archived_chats(
        self,
        page: Optional[int] = None,
        query: Optional[str] = None,
        order_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Optional[List[ChatDetails]]:
        """List archived chats asynchronously."""
        return await self._chat_manager.list_archived_chats(
            page, query, order_by, direction
        )

    async def list_pinned_chats(self) -> Optional[List[ChatDetails]]:
        """List all pinned chats asynchronously."""
        return await self._chat_manager.list_pinned_chats()

    async def pin_chat(self, chat_id: str) -> Optional[ChatDetails]:
        """Toggle pin status of a chat asynchronously."""
        return await self._chat_manager.pin_chat(chat_id)

    async def get_pinned_status(self, chat_id: str) -> Optional[bool]:
        """Check if a chat is pinned asynchronously."""
        return await self._chat_manager.get_pinned_status(chat_id)

    async def archive_chat(self, chat_id: str) -> Optional[ChatDetails]:
        """Toggle archive status of a chat asynchronously."""
        return await self._chat_manager.archive_chat(chat_id)

    async def archive_all_chats(self) -> bool:
        """Archive all chats asynchronously."""
        return await self._chat_manager.archive_all_chats()

    async def unarchive_all_chats(self) -> bool:
        """Restore all archived chats asynchronously."""
        return await self._chat_manager.unarchive_all_chats()

    async def delete_all_chats(self) -> bool:
        """

        ⚠️ WARNING: This is a DESTRUCTIVE operation!
        This method will permanently delete ALL chats associated with the current user account.
        This action CANNOT be undone. Use with extreme caution.

        This method is useful for:
        - Cleaning up test data after integration tests
        - Resetting an account to a clean state
        - Bulk cleanup operations

        Returns:
            True if deletion was successful, False otherwise

        Example:
            ```python
            # ⚠️ WARNING: This will delete ALL your chats!
            success = await client.delete_all_chats()
            if success:
                print("All chats have been permanently deleted")
            ```
        """
        return await self._chat_manager.delete_all_chats()

    # Models
    async def list_models(self):
        return await self._model_manager.list_models()

    async def get_model(self, model_id: str):
        return await self._model_manager.get_model(model_id)

    async def create_model(self, **kwargs):
        return await self._model_manager.create_model(**kwargs)

    async def update_model(self, model_id: str, **kwargs):
        return await self._model_manager.update_model(model_id, **kwargs)

    async def delete_model(self, model_id: str):
        return await self._model_manager.delete_model(model_id)

    # Users
    async def get_users(self, skip: int = 0, limit: int = 50):
        return await self._user_manager.get_users(skip, limit)

    async def get_user_by_id(self, user_id: str):
        return await self._user_manager.get_user_by_id(user_id)

    async def update_user_role(self, user_id: str, role: str):
        return await self._user_manager.update_user_role(user_id, role)

    async def delete_user(self, user_id: str):
        return await self._user_manager.delete_user(user_id)

    # Other
    async def get_prompts(self):
        return await self._prompts_manager.get_prompts()

    # Knowledge Base
    async def get_knowledge_base_by_name(self, name: str):
        return await self._kb_manager.get_knowledge_base_by_name(name)

    async def list_knowledge_bases(self, page: int = 1):
        """List knowledge bases (paginated)."""
        return await self._kb_manager.list_knowledge_bases(page)

    async def search_knowledge_bases(
        self,
        query: Optional[str] = None,
        view_option: Optional[str] = None,
        page: int = 1,
    ):
        """Search KBs by name, description, or owner."""
        return await self._kb_manager.search_knowledge_bases(query, view_option, page)

    async def search_knowledge_files(self, query: Optional[str] = None, page: int = 1):
        """Search files across all accessible knowledge bases."""
        return await self._kb_manager.search_files(query, page)

    async def create_knowledge_base(
        self,
        name: str,
        description: str,
        access_grants: Optional[List[Dict[str, Any]]] = None,
    ):
        """Create a new knowledge base."""
        return await self._kb_manager.create_knowledge_base(
            name, description, access_grants
        )

    async def get_knowledge_base_details(self, kb_id: str):
        """Retrieve a knowledge base by ID including linked files."""
        return await self._kb_manager.get_knowledge_base_details(kb_id)

    async def update_knowledge_base(
        self,
        kb_id: str,
        name: str,
        description: str,
        access_grants: Optional[List[Dict[str, Any]]] = None,
    ):
        """Update name, description, and/or access grants."""
        return await self._kb_manager.update_knowledge_base(
            kb_id, name, description, access_grants
        )

    async def delete_knowledge_base(self, kb_id: str):
        """Permanently delete a knowledge base."""
        return await self._kb_manager.delete_knowledge_base(kb_id)

    async def add_file_to_knowledge_base(self, kb_id: str, file_id: str):
        """Add an already-uploaded file to a knowledge base."""
        return await self._kb_manager.add_file_to_knowledge_base(kb_id, file_id)

    async def batch_add_files_to_kb(self, kb_id: str, file_ids: List[str]):
        """Add multiple files to a knowledge base in a batch."""
        return await self._kb_manager.batch_add_files_to_knowledge_base(kb_id, file_ids)

    async def remove_file_from_knowledge_base(
        self, kb_id: str, file_id: str, delete_file: bool = True
    ):
        """Remove a file from a knowledge base."""
        return await self._kb_manager.remove_file_from_knowledge_base(
            kb_id, file_id, delete_file
        )

    async def upload_file(self, file_path: str):
        return await self._file_manager.upload_file(file_path)

    # Functions
    async def list_functions(self, all: bool = False):
        """List functions. If all is True, requires admin."""
        if all:
            return await self._functions_manager.list_all_functions()
        return await self._functions_manager.list_functions()

    async def upsert_function_from_file(
        self, file_path: str, function_id: Optional[str] = None
    ):
        """Upload/Update a function from a local Python file."""
        return await self._functions_manager.upsert_function_from_file(
            file_path, function_id
        )

    async def diff_functions(self, local_dir: str):
        """Compare local function files (.py) against remote functions."""
        return await self._functions_manager.diff_functions(local_dir)

    async def delete_function(self, function_id: str):
        """Delete a function by ID."""
        return await self._functions_manager.delete_function_by_id(function_id)

    async def update_function_valves(self, function_id: str, valves: Dict[str, Any]):
        """Update global valves for a function."""
        return await self._functions_manager.update_function_valves(function_id, valves)

    async def get_user_valves(self, function_id: str):
        """Get current user valves for a function."""
        return await self._functions_manager.get_user_valves(function_id)

    async def update_user_valves(self, function_id: str, valves: Dict[str, Any]):
        """Update current user valves for a function."""
        return await self._functions_manager.update_user_valves(function_id, valves)

    # Tools
    async def list_tools(self, with_access_flags: bool = False):
        """List tools. If with_access_flags is True, includes explicit write_access boolean."""
        if with_access_flags:
            return await self._tools_manager.list_tools_with_access()
        return await self._tools_manager.list_tools()

    async def upsert_tool_from_file(
        self, file_path: str, tool_id: Optional[str] = None
    ):
        """Upload/Update a tool from a local Python file."""
        return await self._tools_manager.upsert_tool_from_file(file_path, tool_id)

    async def diff_tools(self, local_dir: str):
        """Compare local tool files (.py) against remote tools."""
        return await self._tools_manager.diff_tools(local_dir)

    async def delete_tool(self, tool_id: str):
        """Delete a tool by ID."""
        return await self._tools_manager.delete_tool_by_id(tool_id)

    async def update_tool_valves(self, tool_id: str, valves: Dict[str, Any]):
        """Update global valves for a tool."""
        return await self._tools_manager.update_tool_valves(tool_id, valves)

    async def get_tool_user_valves(self, tool_id: str):
        """Get current user valves for a tool."""
        return await self._tools_manager.get_user_valves(tool_id)

    async def update_tool_user_valves(self, tool_id: str, valves: Dict[str, Any]):
        """Update current user valves for a tool."""
        return await self._tools_manager.update_user_valves(tool_id, valves)


AsyncOpenWebUIClient.stream_chat._no_model_wrap = True
