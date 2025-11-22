"""
Async Chat management module for OpenWebUI Chat Client.
"""

import logging
import json
from typing import Optional, List, Dict, Any, AsyncGenerator, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.async_base_client import AsyncBaseClient

logger = logging.getLogger(__name__)


class AsyncChatManager:
    """
    Handles async chat operations.
    """

    def __init__(self, base_client: "AsyncBaseClient") -> None:
        self.base_client = base_client

    async def list_chats(self, page: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """List all chats."""
        params = {"page": page} if page is not None else {}
        return await self.base_client._get_json_response("GET", "/api/v1/chats/list", params=params)

    async def chat(
        self,
        question: str,
        chat_title: str,
        model_id: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Send a chat message asynchronously.
        
        Args:
            question: The question or prompt to send
            chat_title: Title of the chat session
            model_id: Model identifier to use (optional, uses default if not provided)
            image_paths: List of image file paths for multimodal input (optional)
            tool_ids: List of tool IDs to enable for this chat (optional)
            **kwargs: Additional keyword arguments reserved for future extensions
                (e.g., folder_name, tags, rag_files, rag_collections, etc.)
        
        Returns:
            Dictionary containing the response and metadata, or None if failed
        """
        self.base_client.model_id = model_id or self.base_client.default_model_id

        # Find or create chat
        await self._find_or_create_chat_by_title(chat_title)

        if not self.base_client.chat_id:
            return None

        # Handle logic similar to sync chat
        return await self._ask(question, image_paths=image_paths, tool_ids=tool_ids)

    async def stream_chat(
        self,
        question: str,
        chat_title: str,
        model_id: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response asynchronously with real-time updates.
        
        Args:
            question: The question or prompt to send
            chat_title: Title of the chat session
            model_id: Model identifier to use (optional, uses default if not provided)
            image_paths: List of image file paths for multimodal input (optional)
            tool_ids: List of tool IDs to enable for this chat (optional)
            **kwargs: Additional keyword arguments reserved for future extensions
                (e.g., folder_name, tags, rag_files, rag_collections, etc.)
        
        Yields:
            String chunks of the response as they are generated
        """
        self.base_client.model_id = model_id or self.base_client.default_model_id

        await self._find_or_create_chat_by_title(chat_title)

        if not self.base_client.chat_id:
            return

        async for chunk in self._ask_stream(question):
            yield chunk

    async def _find_or_create_chat_by_title(self, title: str) -> None:
        """Find or create chat."""
        # Search
        response = await self.base_client._make_request(
            "GET",
            "/api/v1/chats/search",
            params={"text": title}
        )

        found_id = None
        if response:
            chats = response.json()
            matching = [c for c in chats if c.get("title") == title]
            if matching:
                # Sort by updated_at desc
                matching.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
                found_id = matching[0]["id"]

        if found_id:
            await self._load_chat_details(found_id)
        else:
            await self._create_new_chat(title)

    async def _create_new_chat(self, title: str) -> None:
        response = await self.base_client._make_request(
            "POST",
            "/api/v1/chats/new",
            json_data={"chat": {"title": title}}
        )
        if response:
            chat_id = response.json().get("id")
            if chat_id:
                await self._load_chat_details(chat_id)

    async def _load_chat_details(self, chat_id: str) -> bool:
        response = await self.base_client._make_request("GET", f"/api/v1/chats/{chat_id}")
        if response:
            details = response.json()
            if details:
                self.base_client.chat_id = chat_id
                self.base_client.chat_object_from_server = details
                return True
        return False

    async def _ask(
        self,
        question: str,
        image_paths: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:

        chat_core = self.base_client.chat_object_from_server["chat"]
        chat_core["models"] = [self.base_client.model_id]
        chat_core.setdefault("history", {"messages": {}, "currentId": None})

        api_messages = self._build_linear_history_for_api(chat_core)

        # Build user content
        content_parts = [{"type": "text", "text": question}]
        # Images TODO: use AsyncFileManager

        final_content = question if len(content_parts) == 1 else content_parts
        api_messages.append({"role": "user", "content": final_content})

        payload = {
            "model": self.base_client.model_id,
            "messages": api_messages,
            "stream": False,
            "chat_id": self.base_client.chat_id
        }

        response = await self.base_client._make_request(
            "POST",
            "/api/chat/completions",
            json_data=payload,
            timeout=300
        )

        if not response:
            return None

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Store messages locally (simplified for brevity)
        # Ideally we replicate the logic of updating local history and sending update to server

        # Return result
        return {"response": content}

    async def _ask_stream(self, question: str) -> AsyncGenerator[str, None]:
        chat_core = self.base_client.chat_object_from_server["chat"]
        api_messages = self._build_linear_history_for_api(chat_core)
        api_messages.append({"role": "user", "content": question})

        payload = {
            "model": self.base_client.model_id,
            "messages": api_messages,
            "stream": True,
            "chat_id": self.base_client.chat_id
        }

        # Use httpx stream
        async with self.base_client.client.stream(
            "POST",
            "/api/chat/completions",
            json=payload,
            headers=self.base_client.json_headers
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    if line.startswith("data:"):
                        data_str = line[len("data:"):].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to decode JSON from stream: {e}. Data: {data_str}")
                        except Exception as e:
                            logger.error(f"Unexpected error while processing stream data: {e}", exc_info=True)

    def _build_linear_history_for_api(self, chat_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Same as sync version
        history = chat_data.get("history", {})
        messages = history.get("messages", {})
        current_id = history.get("currentId")

        linear_messages = []
        if not current_id:
            return linear_messages

        message_chain = []
        msg_id = current_id
        while msg_id and msg_id in messages:
            message_chain.append(messages[msg_id])
            msg_id = messages[msg_id].get("parentId")

        message_chain.reverse()

        for msg in message_chain:
            if msg.get("role") in ["user", "assistant"]:
                linear_messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", "")
                })

        return linear_messages
