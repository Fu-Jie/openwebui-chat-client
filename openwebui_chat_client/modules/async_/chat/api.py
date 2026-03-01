"""Async Chat API Layer - Direct HTTP Interface to Open WebUI Backend."""

import logging
from typing import Any, Dict, List, Optional, AsyncGenerator
import httpx

from openwebui_chat_client.core.async_base_client import AsyncBaseClient
from openwebui_chat_client.modules.chat.types import (
    ChatDict,
    CompletionPayloadDict,
    CompletedPayloadDict,
    ResponseDict,
    ChatID,
    MessageID,
)

logger = logging.getLogger(__name__)


class AsyncChatAPI:
    """Async Chat API Layer - Strictly follows Open WebUI Backend API."""

    def __init__(self, base_client: AsyncBaseClient):
        self.base_client = base_client

    async def completion(
        self, payload: CompletionPayloadDict
    ) -> Optional[ResponseDict]:
        """Generate chat completion response (OpenAI-compatible endpoint)."""
        return await self.base_client._get_json_response(
            "POST", "/api/chat/completions", json_data=payload
        )

    async def stream_completion(
        self, payload: CompletionPayloadDict
    ) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion response (OpenAI SSE)."""
        url = "api/chat/completions"
        payload["stream"] = True

        try:
            async with self.base_client.client.stream(
                "POST", url, json=payload, timeout=None
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data = line[len("data: ") :]
                        if data == "[DONE]":
                            break
                        yield data
        except Exception as e:
            logger.error(f"Async streaming completion failed: {e}", exc_info=True)

    async def completed(
        self, payload: CompletedPayloadDict
    ) -> Optional[Dict[str, Any]]:
        """Trigger outlet filters and background tasks after completion."""
        return await self.base_client._get_json_response(
            "POST", "/api/chat/completed", json_data=payload
        )

    async def create_chat(self, payload: Dict[str, Any]) -> Optional[ChatDict]:
        """Create a new chat conversation."""
        return await self.base_client._get_json_response(
            "POST", "/api/v1/chats/new", json_data=payload
        )

    async def get_chat(self, chat_id: ChatID) -> Optional[ChatDict]:
        """Get full details of a specific chat."""
        return await self.base_client._get_json_response(
            "GET", f"/api/v1/chats/{chat_id}"
        )

    async def update_chat(
        self, chat_id: ChatID, payload: Dict[str, Any]
    ) -> Optional[ChatDict]:
        """Update an existing chat (history, metadata)."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}", json_data=payload
        )

    async def delete_chat(self, chat_id: ChatID) -> bool:
        """Delete a chat conversation."""
        response = await self.base_client._make_request(
            "DELETE", f"/api/v1/chats/{chat_id}"
        )
        return response is not None and response.status_code == 200

    async def list_chats(self, page: int = 1) -> List[ChatDict]:
        """List chat conversations with pagination."""
        params = {"page": page}
        resp = await self.base_client._get_json_response(
            "GET", "/api/v1/chats/list", params=params
        )
        return resp if isinstance(resp, list) else []

    async def delete_all_chats(self) -> bool:
        """Permanently delete all user chats (DESTRUCTIVE)."""
        response = await self.base_client._make_request("DELETE", "/api/v1/chats/")
        return response is not None and response.status_code == 200

    async def search_chats(
        self, query: str, page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search chats by text query with special tag filtering support."""
        params = {"text": query}
        if page is not None:
            params["page"] = page
        resp = await self.base_client._get_json_response(
            "GET", "/api/v1/chats/search", params=params
        )
        return resp if isinstance(resp, list) else []

    async def get_archived_chats(
        self,
        page: Optional[int] = None,
        query: Optional[str] = None,
        order_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List archived chats with advanced filtering and sorting."""
        params = {}
        if page is not None:
            params["page"] = page
        if query:
            params["query"] = query
        if order_by:
            params["order_by"] = order_by
        if direction:
            params["direction"] = direction

        resp = await self.base_client._get_json_response(
            "GET", "/api/v1/chats/archived", params=params
        )
        return resp if isinstance(resp, list) else []

    async def get_pinned_chats(self) -> List[Dict[str, Any]]:
        """Retrieve all pinned chats for the current user."""
        resp = await self.base_client._get_json_response("GET", "/api/v1/chats/pinned")
        return resp if isinstance(resp, list) else []

    async def pin_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Toggle pin status of a chat (favorite/star)."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}/pin"
        )

    async def get_pinned_status(self, chat_id: str) -> Optional[bool]:
        """Check if a chat is currently pinned."""
        return await self.base_client._get_json_response(
            "GET", f"/api/v1/chats/{chat_id}/pinned"
        )

    async def archive_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Toggle archive status of a chat (soft delete)."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/chats/{chat_id}/archive"
        )

    async def archive_all_chats(self) -> bool:
        """Archive all user chats in bulk (mass soft delete)."""
        response = await self.base_client._make_request(
            "POST", "/api/v1/chats/archive/all"
        )
        return response is not None and response.status_code == 200

    async def unarchive_all_chats(self) -> bool:
        """Restore all archived chats to active status (bulk unarchive)."""
        response = await self.base_client._make_request(
            "POST", "/api/v1/chats/unarchive/all"
        )
        return response is not None and response.status_code == 200
