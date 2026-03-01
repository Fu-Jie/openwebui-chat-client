"""Async Chat Manager - High-level Facade for Chat Operations."""

import logging
from typing import Any, Dict, List, Optional, AsyncGenerator, TYPE_CHECKING

from openwebui_chat_client.models import ChatResponse, ChatDetails, Function
from .api import AsyncChatAPI
from .workflow import AsyncChatWorkflow

if TYPE_CHECKING:
    from openwebui_chat_client.core.async_base_client import AsyncBaseClient

logger = logging.getLogger(__name__)


class AsyncChatManager:
    """Async Chat Manager - Coordinates API and Workflow layers."""

    def __init__(self, base_client: "AsyncBaseClient"):
        self.base_client = base_client
        self.api = AsyncChatAPI(base_client)
        self.workflow = AsyncChatWorkflow(self.api)

    async def chat(
        self,
        question: str,
        chat_id: Optional[str] = None,
        chat_title: Optional[str] = None,
        model_id: Optional[str] = None,
        parent_message_id: Optional[str] = None,
        tool_ids: Optional[List[str]] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Optional[ChatResponse]:
        """Send a chat message asynchronously."""
        model = model_id or self.base_client.default_model_id

        result = await self.workflow.execute_full_turn(
            question=question,
            chat_id=chat_id,
            model=model,
            chat_title=chat_title,
            parent_message_id=parent_message_id,
            tool_ids=tool_ids,
            files=files,
            stream=False,
            **kwargs,
        )

        if result and result.get("success"):
            return self._result_to_response(result)
        return None

    async def stream_chat(
        self,
        question: str,
        chat_id: Optional[str] = None,
        chat_title: Optional[str] = None,
        model_id: Optional[str] = None,
        parent_message_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response asynchronously (Bypassing workflow for now to ensure raw yield)."""
        model = model_id or self.base_client.default_model_id

        # Note: Streaming in async needs a more complex orchestrator if we want persistence.
        # For parity with Phase 1 sync logic, we ensure raw SSE data is yielded.
        # Persistence will be handled in a follow-up logic if needed.

        # Build minimal payload for streaming
        from openwebui_chat_client.modules.chat.payloads import ChatPayloads

        user_msg = ChatPayloads.build_user_message(
            content=question, model=model, parent_id=parent_message_id
        )

        payload = ChatPayloads.build_completion_payload(
            model=model,
            messages=[user_msg],
            chat_id=chat_id,
            message_id=user_msg["id"],
            parent_message_id=parent_message_id,
            stream=True,
            **kwargs,
        )

        async for chunk in self.api.stream_completion(payload):
            yield chunk

    async def regenerate_message(
        self,
        chat_id: str,
        parent_message_id: str,
        model_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[ChatResponse]:
        """Regenerate assistant response asynchronously."""
        model = model_id or self.base_client.default_model_id
        result = await self.workflow.regenerate_message(
            chat_id=chat_id, parent_message_id=parent_message_id, model=model, **kwargs
        )
        if result and result.get("success"):
            return self._result_to_response(result)
        return None

    async def edit_message(
        self,
        chat_id: str,
        message_id: str,
        new_content: str,
        model_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[ChatResponse]:
        """Edit user message and trigger new response asynchronously."""
        model = model_id or self.base_client.default_model_id
        result = await self.workflow.edit_message(
            chat_id=chat_id,
            message_id=message_id,
            new_content=new_content,
            model=model,
            **kwargs,
        )
        if result and result.get("success"):
            return self._result_to_response(result)
        return None

    async def delete_all_chats(self) -> bool:
        """Permanently delete ALL chats for the user (IRREVERSIBLE)."""
        return await self.api.delete_all_chats()

    async def search_chats(
        self, query: str, page: Optional[int] = None
    ) -> List[ChatDetails]:
        """Search chats by text query."""
        chats = await self.api.search_chats(query, page)
        return [ChatDetails.from_dict(c) for c in chats]

    async def list_archived_chats(
        self,
        page: Optional[int] = None,
        query: Optional[str] = None,
        order_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[ChatDetails]:
        """List archived chats with filtering."""
        chats = await self.api.get_archived_chats(page, query, order_by, direction)
        return [ChatDetails.from_dict(c) for c in chats]

    async def list_pinned_chats(self) -> List[ChatDetails]:
        """List all pinned chats."""
        chats = await self.api.get_pinned_chats()
        return [ChatDetails.from_dict(c) for c in chats]

    async def pin_chat(self, chat_id: str) -> Optional[ChatDetails]:
        """Toggle pin status of a chat."""
        chat_data = await self.api.pin_chat(chat_id)
        if chat_data:
            return ChatDetails.from_dict(chat_data)
        return None

    async def get_pinned_status(self, chat_id: str) -> Optional[bool]:
        """Check if a chat is pinned."""
        return await self.api.get_pinned_status(chat_id)

    async def archive_chat(self, chat_id: str) -> Optional[ChatDetails]:
        """Toggle archive status of a chat."""
        chat_data = await self.api.archive_chat(chat_id)
        if chat_data:
            return ChatDetails.from_dict(chat_data)
        return None

    async def archive_all_chats(self) -> bool:
        """Archive all chats."""
        return await self.api.archive_all_chats()

    async def unarchive_all_chats(self) -> bool:
        """Restore all archived chats."""
        return await self.api.unarchive_all_chats()

    async def trigger_action(
        self,
        action_id: str,
        chat_id: str,
        message_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Trigger an action for a message."""
        payload = {"id": action_id, "message_id": message_id, **(params or {})}
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}/actions", json_data=payload
        )

    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat asynchronously."""
        return await self.api.delete_chat(chat_id)

    async def list_chats(self, page: int = 1) -> List[ChatDetails]:
        """List chats asynchronously."""
        chats = await self.api.list_chats(page=page)
        return [ChatDetails.from_dict(c) for c in chats]

    async def get_chat(self, chat_id: str) -> Optional[ChatDetails]:
        """Get chat details asynchronously."""
        chat_data = await self.api.get_chat(chat_id)
        if chat_data:
            return ChatDetails.from_dict(chat_data)
        return None

    async def get_functions(self) -> List[Function]:
        """Get available functions asynchronously."""
        resp = await self.base_client._get_json_response("GET", "/api/v1/functions/")
        if resp and isinstance(resp, list):
            return [Function.from_dict(f) for f in resp]
        return []

    def _result_to_response(self, result: Dict[str, Any]) -> ChatResponse:
        """Convert workflow result to ChatResponse object."""
        assistant_msg = result.get("assistant_message", {})
        metadata = result.get("metadata", {})

        content = assistant_msg.get("content") or ""
        return ChatResponse(
            content=content,
            chat_id=result.get("chat_id", ""),
            message_id=assistant_msg.get("id", ""),
            sources=None,
        )
