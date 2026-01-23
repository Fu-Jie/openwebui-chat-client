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
    ModelAccessMixin,
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
)

logger = logging.getLogger(__name__)


class AsyncOpenWebUIClient(ModelAccessMixin):
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

    async def close(self):
        """Close the client."""
        await self._base_client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    # Chat
    async def chat(
        self, question: str, chat_title: str, model_id: Optional[str] = None, **kwargs
    ) -> Optional[ChatResponse]:
        return await self._chat_manager.chat(question, chat_title, model_id, **kwargs)

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
        self, question: str, chat_title: str, model_id: Optional[str] = None, **kwargs
    ) -> AsyncGenerator[str, None]:
        async for chunk in self._chat_manager.stream_chat(
            question, chat_title, model_id, **kwargs
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

    async def delete_all_chats(self) -> bool:
        """
        Delete ALL chat conversations for the current user.

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

    async def get_knowledge_base_by_name(self, name: str):
        return await self._kb_manager.get_knowledge_base_by_name(name)

    async def upload_file(self, file_path: str):
        return await self._file_manager.upload_file(file_path)
