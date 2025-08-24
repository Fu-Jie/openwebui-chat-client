"""
Asynchronous OpenWebUI Chat Client.

An intelligent, stateful async Python client for the Open WebUI API,
built on httpx.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any

from .core.async_base_client import AsyncBaseClient
from .modules.async_model_manager import AsyncModelManager
from .modules.async_chat_manager import AsyncChatManager
from .modules.async_notes_manager import AsyncNotesManager
from .modules.async_knowledge_base_manager import AsyncKnowledgeBaseManager
from .modules.async_file_manager import AsyncFileManager
from .modules.async_prompts_manager import AsyncPromptsManager

logger = logging.getLogger(__name__)


class AsyncOpenWebUIClient:
    """
    An asynchronous, intelligent, stateful Python client for the Open WebUI API.
    This client uses httpx and asyncio to provide non-blocking API interactions.
    """

    def __init__(self, base_url: str, token: str, default_model_id: str):
        """
        Initializes the client synchronously.

        To properly initialize the async components and refresh models,
        you must call this class via the `AsyncOpenWebUIClient.create()` factory method.

        Example:
            client = await AsyncOpenWebUIClient.create(
                base_url="http://localhost:3000",
                token="your-token",
                default_model_id="gpt-4.1"
            )

        Args:
            base_url: The base URL of the OpenWebUI instance.
            token: Authentication token.
            default_model_id: Default model identifier to use.
        """
        self._base_client = AsyncBaseClient(base_url, token, default_model_id)
        self._model_manager: Optional[AsyncModelManager] = None
        self._chat_manager: Optional[AsyncChatManager] = None
        self._notes_manager: Optional[AsyncNotesManager] = None
        self._kb_manager: Optional[AsyncKnowledgeBaseManager] = None
        self._file_manager: Optional[AsyncFileManager] = None
        self._prompts_manager: Optional[AsyncPromptsManager] = None


    @classmethod
    async def create(
        cls,
        base_url: str,
        token: str,
        default_model_id: str,
        skip_model_refresh: bool = False
    ) -> "AsyncOpenWebUIClient":
        """
        Asynchronously creates and initializes the client instance.
        This is the recommended way to instantiate the client.
        """
        client = cls(base_url, token, default_model_id)

        # Initialize managers
        client._model_manager = AsyncModelManager(client._base_client)
        client._chat_manager = AsyncChatManager(client._base_client)
        client._notes_manager = AsyncNotesManager(client._base_client)
        client._kb_manager = AsyncKnowledgeBaseManager(client._base_client)
        client._file_manager = AsyncFileManager(client._base_client)
        client._prompts_manager = AsyncPromptsManager(client._base_client)

        # Set parent reference for managers to access main client methods if needed
        client._base_client._parent_client = client

        if not skip_model_refresh:
            await client._model_manager.refresh_available_models()

        return client

    @property
    def models(self) -> AsyncModelManager:
        """Access the model manager."""
        if not self._model_manager:
            raise RuntimeError("Client not fully initialized. Please use await AsyncOpenWebUIClient.create()")
        return self._model_manager

    @property
    def chat(self) -> AsyncChatManager:
        """Access the chat manager."""
        if not self._chat_manager:
            raise RuntimeError("Client not fully initialized. Please use await AsyncOpenWebUIClient.create()")
        return self._chat_manager

    @property
    def notes(self) -> AsyncNotesManager:
        """Access the notes manager."""
        if not self._notes_manager:
            raise RuntimeError("Client not fully initialized. Please use await AsyncOpenWebUIClient.create()")
        return self._notes_manager

    @property
    def knowledge_base(self) -> AsyncKnowledgeBaseManager:
        """Access the knowledge base manager."""
        if not self._kb_manager:
            raise RuntimeError("Client not fully initialized. Please use await AsyncOpenWebUIClient.create()")
        return self._kb_manager

    @property
    def files(self) -> AsyncFileManager:
        """Access the file manager."""
        if not self._file_manager:
            raise RuntimeError("Client not fully initialized. Please use await AsyncOpenWebUIClient.create()")
        return self._file_manager

    @property
    def prompts(self) -> AsyncPromptsManager:
        """Access the prompts manager."""
        if not self._prompts_manager:
            raise RuntimeError("Client not fully initialized. Please use await AsyncOpenWebUIClient.create()")
        return self._prompts_manager

    async def close(self):
        """Cleanly close the underlying httpx session."""
        await self._base_client.close()

    def __await__(self):
        """Allows for `await AsyncOpenWebUIClient(...)` syntax."""
        # This is a bit of syntactic sugar. It's not standard,
        # but can be a nice touch. The `create` classmethod is more explicit.
        # For now, we will stick to the explicit classmethod.
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
