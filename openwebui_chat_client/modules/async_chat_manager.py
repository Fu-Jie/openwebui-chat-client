"""
Async Chat management module for OpenWebUI Chat Client.
"""

import asyncio
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

    async def list_chats(
        self, page: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """List all chats."""
        params = {"page": page} if page is not None else {}
        return await self.base_client._get_json_response(
            "GET", "/api/v1/chats/list", params=params
        )

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
            >>> # ⚠️ WARNING: This will delete ALL your chats!
            >>> success = await client.delete_all_chats()
            >>> if success:
            ...     print("All chats have been permanently deleted")
        """
        logger.warning("⚠️ DELETING ALL CHATS - This action cannot be undone!")

        try:
            response = await self.base_client._make_request(
                "DELETE", "/api/v1/chats/", timeout=30
            )

            if response and response.status_code == 200:
                logger.info("✅ Successfully deleted all chats")
                return True
            else:
                logger.error(
                    f"❌ Failed to delete all chats: {response.status_code if response else 'No response'}"
                )
                return False
        except Exception as e:
            logger.error(f"❌ Failed to delete all chats: {e}")
            return False

    async def chat(
        self,
        question: str,
        chat_title: str,
        model_id: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a chat message asynchronously.

        Args:
            question: The question or prompt to send
            chat_title: Title of the chat session
            model_id: Model identifier to use (optional, uses default if not provided)
            image_paths: List of image file paths for multimodal input (optional)
            rag_files: List of file paths for RAG (optional)
            rag_collections: List of knowledge base collection names for RAG (optional)
            tool_ids: List of tool IDs to enable for this chat (optional)
            **kwargs: Additional keyword arguments reserved for future extensions
                (e.g., folder_name, tags, rag_files, rag_collections, etc.)

        Returns:
            Dictionary containing the response and metadata, or None if failed
        """
        current_model_id = model_id or self.base_client.default_model_id

        # Find or create chat - get local copies for concurrency safety
        chat_id, chat_object = await self._find_or_create_chat_by_title(chat_title)

        if not chat_id or not chat_object:
            return None

        # Handle logic similar to sync chat, passing local copies
        return await self._ask(
            question,
            chat_id,
            chat_object,
            current_model_id,
            image_paths=image_paths,
            rag_files=rag_files,
            rag_collections=rag_collections,
            tool_ids=tool_ids,
        )

    async def stream_chat(
        self,
        question: str,
        chat_title: str,
        model_id: Optional[str] = None,
        folder_name: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_follow_up: bool = False,
        cleanup_placeholder_messages: bool = False,
        placeholder_pool_size: int = 30,
        min_available_messages: int = 10,
        wait_before_request: float = 10.0,
        enable_auto_tagging: bool = False,
        enable_auto_titling: bool = False,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response asynchronously with real-time updates.

        Args:
            question: The question or prompt to send
            chat_title: Title of the chat session
            model_id: Model identifier to use (optional, uses default if not provided)
            folder_name: Folder name to organize the chat (optional)
            image_paths: List of image file paths for multimodal input (optional)
            tags: List of tags to apply to the chat (optional)
            rag_files: List of file paths for RAG (optional)
            rag_collections: List of knowledge base collection names for RAG (optional)
            tool_ids: List of tool IDs to enable for this chat (optional)
            enable_follow_up: Whether to generate follow-up suggestions (optional)
            cleanup_placeholder_messages: Whether to cleanup unused placeholder messages (optional)
            placeholder_pool_size: Target size for placeholder message pool (optional)
            min_available_messages: Minimum available messages before creating more (optional)
            wait_before_request: Time to wait before request (optional)
            enable_auto_tagging: Whether to auto-generate tags (optional)
            enable_auto_titling: Whether to auto-generate title (optional)

        Yields:
            String chunks of the response as they are generated
        """
        current_model_id = model_id or self.base_client.default_model_id

        # Log request details (matching sync version)
        logger.info("=" * 60)
        logger.info(
            f"Processing STREAMING request: title='{chat_title}', model='{current_model_id}'"
        )
        if folder_name:
            logger.info(f"Folder: '{folder_name}'")
        if tags:
            logger.info(f"Tags: {tags}")
        if image_paths:
            logger.info(f"With images: {image_paths}")
        if rag_files:
            logger.info(f"With RAG files: {rag_files}")
        if rag_collections:
            logger.info(f"With KB collections: {rag_collections}")
        if tool_ids:
            logger.info(f"Using tools: {tool_ids}")
        logger.info("=" * 60)

        # Find or create chat - get local copies for concurrency safety
        chat_id, chat_object = await self._find_or_create_chat_by_title(chat_title)

        if not chat_id or not chat_object:
            return

        # Handle placeholder messages (matching sync version)
        if cleanup_placeholder_messages:
            self._cleanup_unused_placeholder_messages(chat_object)

        await self._ensure_placeholder_messages(
            chat_id, chat_object, placeholder_pool_size, min_available_messages
        )

        # First-stream delay (match sync behavior)
        if (
            getattr(self.base_client, "_first_stream_request", True)
            and wait_before_request > 0
        ):
            logger.info(
                f"⏱️ First stream request: waiting {wait_before_request} seconds before requesting AI response..."
            )
            await asyncio.sleep(wait_before_request)
            self.base_client._first_stream_request = False

        # Apply folder placement if requested
        if folder_name:
            await self._ensure_folder(chat_id, folder_name)

        full_response = ""
        async for chunk in self._ask_stream(
            question,
            chat_id,
            chat_object,
            current_model_id,
            image_paths=image_paths,
            rag_files=rag_files,
            rag_collections=rag_collections,
            tool_ids=tool_ids,
            enable_follow_up=enable_follow_up,
        ):
            full_response += chunk
            yield chunk

        chat_core = chat_object["chat"]
        user_message_id = chat_core.get("_last_stream_user_id")
        assistant_message_id = chat_core.get("_last_stream_assistant_id")

        if assistant_message_id and user_message_id:
            # finalize message flags
            for mid in (user_message_id, assistant_message_id):
                message = chat_core.get("history", {}).get("messages", {}).get(mid, {})
                message.pop("_is_placeholder", None)
                message.pop("_is_available", None)
            # update current pointer and linear history
            chat_core["history"]["currentId"] = assistant_message_id
            chat_core["messages"] = self._build_linear_history_for_storage(
                chat_core, assistant_message_id
            )
            chat_core["models"] = [current_model_id]

            # merge stored file references into chat files
            chat_core.setdefault("files", [])
            existing_file_ids = {f.get("id") for f in chat_core.get("files", [])}
            storage_user = chat_core["history"]["messages"].get(user_message_id, {})
            for f in storage_user.get("files", []):
                file_id = f.get("id")
                if file_id and file_id not in existing_file_ids:
                    chat_core["files"].append(f)
                    existing_file_ids.add(file_id)

            await self._update_remote_chat(chat_id, chat_core)

        # Tag and metadata updates after stream
        if tags:
            await self._set_chat_tags(chat_id, tags)

        api_messages_for_tasks = self._build_linear_history_for_api(chat_core)
        if enable_auto_tagging:
            suggested_tags = await self._get_tags(api_messages_for_tasks)
            if suggested_tags:
                await self._set_chat_tags(chat_id, suggested_tags)

        if (
            enable_auto_titling
            and len(chat_core.get("history", {}).get("messages", {})) <= 2
        ):
            suggested_title = await self._get_title(api_messages_for_tasks)
            if suggested_title:
                await self._rename_chat(chat_id, suggested_title)

    async def _find_or_create_chat_by_title(self, title: str) -> tuple:
        """Find or create chat. Returns (chat_id, chat_object) tuple for concurrency safety."""
        # Search
        response = await self.base_client._make_request(
            "GET", "/api/v1/chats/search", params={"text": title}
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
            return await self._load_chat_details(found_id)
        else:
            return await self._create_new_chat(title)

    async def _create_new_chat(self, title: str) -> tuple:
        """Create a new chat. Returns (chat_id, chat_object) tuple."""
        response = await self.base_client._make_request(
            "POST", "/api/v1/chats/new", json_data={"chat": {"title": title}}
        )
        if response:
            chat_id = response.json().get("id")
            if chat_id:
                return await self._load_chat_details(chat_id)
        return (None, None)

    async def _load_chat_details(self, chat_id: str, max_retries: int = 3, retry_delay: float = 1.0) -> tuple:
        """Load chat details. Returns (chat_id, chat_object) tuple.
        
        Args:
            chat_id: The ID of the chat to load
            max_retries: Maximum number of retries for transient errors (default: 3)
            retry_delay: Delay in seconds between retries (default: 1.0)
        """
        import httpx
        
        last_error = None
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Retry attempt {attempt + 1}/{max_retries} after {retry_delay}s delay...")
                    await asyncio.sleep(retry_delay)
                
                url = f"/api/v1/chats/{chat_id}".lstrip('/')
                response = await self.base_client.client.get(
                    url,
                    headers=self.base_client.json_headers,
                    timeout=30
                )
                
                # Handle 401 errors with retry (can be transient after chat creation)
                if response.status_code == 401:
                    logger.warning(f"⚠️ Got 401 Unauthorized on attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        last_error = "401 Unauthorized"
                        continue  # Retry
                    else:
                        response.raise_for_status()
                
                response.raise_for_status()
                
                details = response.json()
                if details:
                    # Also update shared state for backward compatibility
                    self.base_client.chat_id = chat_id
                    self.base_client.chat_object_from_server = details
                    return (chat_id, details)
                return (None, None)
                
            except httpx.TimeoutException as e:
                logger.error(f"❌ Chat details load timeout: {e}")
                last_error = str(e)
                if attempt < max_retries - 1:
                    continue
                return (None, None)
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ Chat details load HTTP error {e.response.status_code}: {e}")
                return (None, None)
            except httpx.RequestError as e:
                logger.error(f"❌ Chat details load request error: {e}")
                last_error = str(e)
                if attempt < max_retries - 1:
                    continue
                return (None, None)
            except Exception as e:
                logger.error(f"❌ Unexpected error loading chat details: {e}")
                return (None, None)
        
        logger.error(f"❌ Failed to load chat details after {max_retries} attempts. Last error: {last_error}")
        return (None, None)

    async def _ask(
        self,
        question: str,
        chat_id: str,
        chat_object: Dict[str, Any],
        model_id: str,
        image_paths: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        import uuid
        import time

        # Use local copy of chat_core for concurrency safety
        chat_core = chat_object["chat"]
        chat_core["models"] = [model_id]
        chat_core.setdefault("history", {"messages": {}, "currentId": None})
        chat_core.setdefault("files", [])

        api_messages = self._build_linear_history_for_api(chat_core)

        # Handle RAG references
        api_rag_payload, storage_rag_payloads = await self._handle_rag_references(
            rag_files, rag_collections
        )

        # Build user content
        content_parts = [{"type": "text", "text": question}]
        if image_paths:
            for image_path in image_paths:
                base64_image = self._encode_image_to_base64(image_path)
                if base64_image:
                    content_parts.append(
                        {"type": "image_url", "image_url": {"url": base64_image}}
                    )

        final_content = question if len(content_parts) == 1 else content_parts
        api_messages.append({"role": "user", "content": final_content})

        payload = {
            "model": model_id,
            "messages": api_messages,
            "stream": False,
            "chat_id": chat_id,
            "parent_message": {},
        }

        if api_rag_payload:
            payload["files"] = api_rag_payload
        if tool_ids:
            payload["tool_ids"] = tool_ids

        response = await self.base_client._make_request(
            "POST", "/api/chat/completions", json_data=payload, timeout=300
        )

        if not response:
            return None

        data = response.json()
        assistant_content = data["choices"][0]["message"]["content"]

        # Build and store messages
        user_message_id = str(uuid.uuid4())
        last_message_id = chat_core["history"].get("currentId")

        storage_user_message = {
            "id": user_message_id,
            "parentId": last_message_id,
            "childrenIds": [],
            "role": "user",
            "content": question,
            "files": [],
            "models": [model_id],
            "timestamp": int(time.time()),
        }

        # Attach RAG storage payloads and images to user message
        storage_user_message["files"].extend(storage_rag_payloads)
        if image_paths:
            for image_path in image_paths:
                base64_url = self._encode_image_to_base64(image_path)
                if base64_url:
                    storage_user_message["files"].append(
                        {"type": "image", "url": base64_url}
                    )

        chat_core["history"]["messages"][user_message_id] = storage_user_message
        if last_message_id and last_message_id in chat_core["history"]["messages"]:
            chat_core["history"]["messages"][last_message_id]["childrenIds"].append(
                user_message_id
            )

        assistant_message_id = str(uuid.uuid4())
        storage_assistant_message = {
            "id": assistant_message_id,
            "parentId": user_message_id,
            "childrenIds": [],
            "role": "assistant",
            "content": assistant_content,
            "model": model_id,
            "modelName": model_id.split(":")[0],
            "timestamp": int(time.time()),
            "done": True,
            "sources": [],
        }
        chat_core["history"]["messages"][
            assistant_message_id
        ] = storage_assistant_message
        chat_core["history"]["messages"][user_message_id]["childrenIds"].append(
            assistant_message_id
        )

        # Update current ID and build linear history for storage
        chat_core["history"]["currentId"] = assistant_message_id
        chat_core["messages"] = self._build_linear_history_for_storage(
            chat_core, assistant_message_id
        )
        chat_core["models"] = [model_id]

        # Merge unique file ids into chat_core files (RAG and images)
        existing_file_ids = {f.get("id") for f in chat_core.get("files", [])}
        chat_core.setdefault("files", []).extend(
            [f for f in storage_rag_payloads if f.get("id") not in existing_file_ids]
        )

        # Update remote chat to persist the conversation, using local chat_id and chat_core
        await self._update_remote_chat(chat_id, chat_core)

        return {
            "response": assistant_content,
            "chat_id": chat_id,
            "message_id": assistant_message_id,
        }

    async def _ask_stream(
        self,
        question: str,
        chat_id: str,
        chat_object: Dict[str, Any],
        model_id: str,
        image_paths: Optional[List[str]] = None,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
        tool_ids: Optional[List[str]] = None,
        enable_follow_up: bool = False,
    ) -> AsyncGenerator[str, None]:
        import uuid
        import time

        # Use local copy of chat_core for concurrency safety
        chat_core = chat_object["chat"]
        chat_core["models"] = [model_id]

        # 1. Get placeholder message pair
        message_pair = self._get_next_available_message_pair(chat_object)
        if not message_pair:
            logger.error(
                "No available placeholder message pairs after ensuring, cannot proceed with stream."
            )
            return

        user_message_id, assistant_message_id = message_pair

        # 2. Prepare API messages
        api_rag_payload, storage_rag_payloads = await self._handle_rag_references(
            rag_files, rag_collections
        )

        api_messages = self._build_linear_history_for_api(chat_core)

        current_user_content_parts = [{"type": "text", "text": question}]
        if image_paths:
            for image_path in image_paths:
                base64_image = self._encode_image_to_base64(image_path)
                if base64_image:
                    current_user_content_parts.append(
                        {"type": "image_url", "image_url": {"url": base64_image}}
                    )

        final_api_content = (
            question
            if len(current_user_content_parts) == 1
            else current_user_content_parts
        )

        api_messages.append({"role": "user", "content": final_api_content})

        payload = {
            "model": model_id,
            "messages": api_messages,
            "stream": True,
            "chat_id": chat_id,
            "parent_message": {},
        }

        if api_rag_payload:
            payload["files"] = api_rag_payload

        if tool_ids:
            payload["tool_ids"] = tool_ids

        # 3. Update local storage placeholder message content
        messages = chat_core["history"]["messages"]
        storage_user_message = messages[user_message_id]
        storage_assistant_message = messages[assistant_message_id]

        storage_user_message["content"] = question
        storage_user_message["models"] = [model_id]
        storage_user_message["timestamp"] = int(time.time())

        # Update files in storage
        storage_user_message["files"] = []
        if image_paths:
            for image_path in image_paths:
                base64_url = self._encode_image_to_base64(image_path)
                if base64_url:
                    storage_user_message["files"].append(
                        {"type": "image", "url": base64_url}
                    )
        storage_user_message["files"].extend(storage_rag_payloads)

        storage_assistant_message["content"] = ""
        storage_assistant_message["model"] = model_id
        storage_assistant_message["modelName"] = model_id.split(":")[0]
        storage_assistant_message["timestamp"] = int(time.time())
        storage_assistant_message["done"] = False
        storage_assistant_message["sources"] = []
        storage_assistant_message["_is_placeholder"] = False
        storage_assistant_message["_is_available"] = False
        storage_user_message["_is_placeholder"] = False
        storage_user_message["_is_available"] = False

        # 4. Update user message content via delta event
        await self._stream_delta_update(chat_id, user_message_id, question)

        # 5. Start streaming
        full_response = ""

        try:
            async with self.base_client.client.stream(
                "POST",
                "/api/chat/completions",
                json=payload,
                headers=self.base_client.json_headers,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        if line.startswith("data:"):
                            data_str = line[len("data:") :].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and data["choices"]:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        chunk = delta["content"]
                                        if chunk is None:
                                            continue
                                        if not isinstance(chunk, str):
                                            chunk = str(chunk)
                                        full_response += chunk
                                        yield chunk

                                        # Update assistant message content incrementally
                                        storage_assistant_message["content"] = (
                                            full_response
                                        )
                                        # Send delta update
                                        await self._stream_delta_update(
                                            chat_id, assistant_message_id, chunk
                                        )

                            except json.JSONDecodeError as e:
                                logger.warning(
                                    f"Failed to decode JSON from stream: {e}. Data: {data_str}"
                                )
                            except Exception as e:
                                logger.error(
                                    f"Unexpected error while processing stream data: {e}",
                                    exc_info=True,
                                )

            # 6. Finalize
            storage_assistant_message["content"] = full_response
            storage_assistant_message["done"] = True
            chat_core["history"]["currentId"] = assistant_message_id
            chat_core["messages"] = self._build_linear_history_for_storage(
                chat_core, assistant_message_id
            )
            chat_core["models"] = [model_id]
            chat_core["_last_stream_user_id"] = user_message_id
            chat_core["_last_stream_assistant_id"] = assistant_message_id
            chat_core.setdefault("files", [])
            existing_file_ids = {f.get("id") for f in chat_core.get("files", [])}
            for f in storage_user_message.get("files", []):
                fid = f.get("id")
                if fid and fid not in existing_file_ids:
                    chat_core["files"].append(f)
                    existing_file_ids.add(fid)

            # Note: We do NOT call _update_remote_chat here, matching sync client behavior.
            # The content has been updated via delta events, and the structure was saved when placeholders were created.

        except Exception as e:
            logger.error(f"Error during streaming: {e}")

        # Follow-up suggestions (optional)
        if enable_follow_up:
            try:
                api_messages_for_follow_up = self._build_linear_history_for_api(
                    chat_core
                )
                follow_ups = await self._get_follow_up_completions(
                    api_messages_for_follow_up
                )
                if follow_ups:
                    storage_assistant_message["followUps"] = follow_ups
                    await self._update_remote_chat(chat_id, chat_core)
            except Exception as e:
                logger.error(f"❌ Error processing follow-ups: {e}")

    async def _update_remote_chat(
        self, chat_id: str, chat_data: Dict[str, Any]
    ) -> bool:
        """Update remote chat on server using provided chat_id and chat_data for concurrency safety."""
        if not chat_id or not chat_data:
            logger.error("Missing chat_id or chat_data")
            return False

        try:
            response = await self.base_client._make_request(
                "POST",
                f"/api/v1/chats/{chat_id}",
                json_data={"chat": chat_data},
                timeout=30,
            )

            if response and response.status_code == 200:
                logger.debug(f"Chat history updated successfully for chat {chat_id}")
                return True
            else:
                logger.warning(
                    f"Failed to update chat history: {response.status_code if response else 'No response'}"
                )
                return False

        except Exception as e:
            logger.error(f"Error updating remote chat: {e}")
            return False

    def _build_linear_history_for_api(
        self, chat_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build linear message history for API calls."""
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
                linear_messages.append(
                    {"role": msg["role"], "content": msg.get("content", "")}
                )

        return linear_messages

    def _build_linear_history_for_storage(
        self, chat_data: Dict[str, Any], final_msg_id: str
    ) -> List[Dict[str, Any]]:
        """Build linear message history for storage format."""
        history = chat_data.get("history", {})
        messages = history.get("messages", {})

        linear_messages = []

        message_chain = []
        msg_id = final_msg_id
        while msg_id and msg_id in messages:
            message_chain.append(messages[msg_id])
            msg_id = messages[msg_id].get("parentId")

        message_chain.reverse()

        for msg in message_chain:
            storage_msg = {
                "id": msg.get("id"),
                "parentId": msg.get("parentId"),
                "childrenIds": msg.get("childrenIds", []),
                "role": msg.get("role"),
                "content": msg.get("content", ""),
            }
            if msg.get("role") == "assistant":
                storage_msg["model"] = msg.get("model")
                storage_msg["modelName"] = msg.get("modelName")
                storage_msg["done"] = msg.get("done", True)
            linear_messages.append(storage_msg)

        return linear_messages

    # --- Placeholder Message Management ---

    def _is_placeholder_message(self, message: Dict[str, Any]) -> bool:
        """Check if message is a placeholder (content is empty and not marked as done)"""
        return message.get("content", "").strip() == "" and not message.get(
            "done", False
        )

    def _count_available_placeholder_pairs(self, chat_object: Dict[str, Any]) -> int:
        """Count the number of available placeholder message pairs."""
        messages = chat_object["chat"].get("history", {}).get("messages", {})
        available_pairs = 0

        for message in messages.values():
            if (
                message.get("_is_placeholder")
                and message.get("_is_available")
                and message.get("role") == "user"
            ):
                # Check if corresponding assistant message is also available
                children = message.get("childrenIds", [])
                if children:
                    assistant_message = messages.get(children[0])
                    if (
                        assistant_message
                        and assistant_message.get("_is_placeholder")
                        and assistant_message.get("_is_available")
                    ):
                        available_pairs += 1

        return available_pairs

    async def _ensure_placeholder_messages(
        self,
        chat_id: str,
        chat_object: Dict[str, Any],
        pool_size: int,
        min_available: int,
    ) -> bool:
        """
        Ensures there are enough placeholder message pairs available for streaming.
        Creates placeholder pairs that form a proper multi-turn conversation chain.
        """
        import uuid
        import time

        chat_core = chat_object["chat"]
        chat_core.setdefault("history", {"messages": {}, "currentId": None})

        # Count available placeholder pairs
        available_pairs = self._count_available_placeholder_pairs(chat_object)

        if available_pairs >= min_available:
            return True

        pairs_to_create = pool_size - available_pairs
        if pairs_to_create <= 0:
            return True

        logger.info(
            f"Creating {pairs_to_create} placeholder message pairs (current: {available_pairs}, target: {pool_size})..."
        )

        # Find the last real message (not placeholder or used placeholder)
        messages = chat_core["history"]["messages"]
        current_id = chat_core["history"].get("currentId")

        last_message_id = current_id

        for _ in range(pairs_to_create):
            # Create User Placeholder
            user_id = str(uuid.uuid4())
            user_message = {
                "id": user_id,
                "parentId": last_message_id,
                "childrenIds": [],
                "role": "user",
                "content": "",
                "models": [],
                "timestamp": int(time.time()),
                "_is_placeholder": True,
                "_is_available": True,
            }

            messages[user_id] = user_message
            if last_message_id and last_message_id in messages:
                messages[last_message_id]["childrenIds"].append(user_id)

            # Create Assistant Placeholder
            assistant_id = str(uuid.uuid4())
            assistant_message = {
                "id": assistant_id,
                "parentId": user_id,
                "childrenIds": [],
                "role": "assistant",
                "content": "",
                "models": [],
                "timestamp": int(time.time()),
                "done": False,
                "_is_placeholder": True,
                "_is_available": True,
            }

            messages[assistant_id] = assistant_message
            messages[user_id]["childrenIds"].append(assistant_id)

            last_message_id = assistant_id

        # Update currentId to the last created placeholder
        if last_message_id:
            chat_core["history"]["currentId"] = last_message_id
            # Update the linear messages array
            chat_core["messages"] = self._build_linear_history_for_storage(
                chat_core, last_message_id
            )

        # Persist the new placeholders to server (Matching sync behavior)
        await self._update_remote_chat(chat_id, chat_core)

        logger.info(
            f"✅ Created {pairs_to_create} placeholder message pairs in conversation chain."
        )
        return True

    def _cleanup_unused_placeholder_messages(self, chat_object: Dict[str, Any]) -> int:
        """Remove unused placeholder message pairs."""
        chat_core = chat_object["chat"]
        messages = chat_core.get("history", {}).get("messages", {})
        cleaned_count = 0

        # Find placeholder pairs that are still available (unused)
        pairs_to_remove = []
        for message in messages.values():
            if (
                message.get("_is_placeholder")
                and message.get("_is_available")
                and message.get("role") == "user"
            ):

                children = message.get("childrenIds", [])
                if children:
                    assistant_id = children[0]
                    assistant_message = messages.get(assistant_id)
                    if (
                        assistant_message
                        and assistant_message.get("_is_placeholder")
                        and assistant_message.get("_is_available")
                    ):
                        pairs_to_remove.append((message["id"], assistant_id))

        # Remove the pairs
        for user_id, assistant_id in pairs_to_remove:
            if user_id in messages:
                del messages[user_id]
                cleaned_count += 1
            if assistant_id in messages:
                del messages[assistant_id]

        if cleaned_count > 0:
            logger.info(
                f"🧹 Cleaned up {cleaned_count} unused placeholder message pairs."
            )

        return cleaned_count

    def _get_next_available_message_pair(
        self, chat_object: Dict[str, Any]
    ) -> Optional[tuple]:
        """Get the next available placeholder message pair."""
        messages = chat_object["chat"].get("history", {}).get("messages", {})

        for message in messages.values():
            if (
                message.get("_is_placeholder")
                and message.get("_is_available")
                and message.get("role") == "user"
            ):
                children = message.get("childrenIds", [])
                if children:
                    assistant_id = children[0]
                    assistant_message = messages.get(assistant_id)
                    if (
                        assistant_message
                        and assistant_message.get("_is_placeholder")
                        and assistant_message.get("_is_available")
                    ):
                        # Mark as used
                        message["_is_available"] = False
                        assistant_message["_is_available"] = False
                        return message["id"], assistant_id

        return None

    async def _stream_delta_update(
        self, chat_id: str, message_id: str, delta_content: str
    ) -> None:
        """
        Push incremental content in real-time to the specified message of the specified chat.
        """
        if not delta_content.strip():
            return

        url = f"/api/v1/chats/{chat_id}/messages/{message_id}/event"
        payload = {"type": "chat:message:delta", "data": {"content": delta_content}}

        try:
            # Fire and forget - we don't want to block streaming on this
            # In async, we can just await it with a very short timeout or spawn a task
            # For simplicity in this context, we'll await it but catch errors
            await self.base_client._make_request(
                "POST", url, json_data=payload, timeout=3.0
            )
        except Exception as e:
            logger.debug(f"⚠️ Delta update failed for message {message_id[:8]}...: {e}")

    # --- RAG and Multimodal Helpers ---

    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Encode an image file to base64 format for use in multimodal chat."""
        import base64
        import os

        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None

        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                media_type = "image/jpeg"
                if image_path.lower().endswith(".png"):
                    media_type = "image/png"
                elif image_path.lower().endswith(".gif"):
                    media_type = "image/gif"
                elif image_path.lower().endswith(".webp"):
                    media_type = "image/webp"

                return f"data:{media_type};base64,{encoded_string}"
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None

    async def _handle_rag_references(
        self,
        rag_files: Optional[List[str]] = None,
        rag_collections: Optional[List[str]] = None,
    ) -> tuple:
        """Handle RAG references for files and knowledge base collections."""
        api_payload = []
        storage_payload = []

        if rag_files:
            logger.info("Processing RAG files...")
            for file_path in rag_files:
                file_obj = await self.base_client._upload_file(file_path)
                if file_obj:
                    api_payload.append({"type": "file", "id": file_obj["id"]})
                    storage_payload.append(
                        {"type": "file", "file": file_obj, **file_obj}
                    )

        if rag_collections:
            logger.info("Processing RAG knowledge base collections...")
            # Fetch all KBs to find by name
            kbs_response = await self.base_client._get_json_response(
                "GET", "/api/v1/knowledge/"
            )
            if kbs_response:
                for kb_name in rag_collections:
                    # Find KB by name
                    kb_summary = next(
                        (kb for kb in kbs_response if kb.get("name") == kb_name), None
                    )
                    if kb_summary:
                        # Get details
                        kb_details = await self.base_client._get_json_response(
                            "GET", f"/api/v1/knowledge/{kb_summary['id']}"
                        )
                        if kb_details:
                            file_ids = [f["id"] for f in kb_details.get("files", [])]
                            api_payload.append(
                                {
                                    "type": "collection",
                                    "id": kb_details["id"],
                                    "name": kb_details.get("name"),
                                    "data": {"file_ids": file_ids},
                                }
                            )
                            storage_payload.append(
                                {
                                    "type": "collection",
                                    "collection": kb_details,
                                    **kb_details,
                                }
                            )

        return api_payload, storage_payload

    async def _get_follow_up_completions(
        self, messages: List[Dict[str, Any]]
    ) -> Optional[List[str]]:
        """Generate follow-up suggestions asynchronously."""
        try:
            task_model = await self.base_client._get_task_model()
            if not task_model:
                return None

            payload = {
                "model": task_model,
                "messages": messages,
                "stream": False,
            }

            response = await self.base_client._make_request(
                "POST",
                "/api/v1/tasks/follow-up/completions",
                json_data=payload,
            )

            if not response:
                return None

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            try:
                follow_data = json.loads(content)
                return (
                    follow_data.get("follow_ups") or follow_data.get("followUps") or []
                )
            except json.JSONDecodeError:
                return [line.strip() for line in content.split("\n") if line.strip()]
        except Exception as e:
            logger.error(f"Failed to generate follow-ups: {e}")
            return None

    async def _get_tags(self, messages: List[Dict[str, Any]]) -> Optional[List[str]]:
        """Generate tags for the conversation asynchronously."""
        try:
            task_model = await self.base_client._get_task_model()
            if not task_model:
                return None

            payload = {"model": task_model, "messages": messages, "stream": False}
            response = await self.base_client._make_request(
                "POST",
                "/api/v1/tasks/tags/completions",
                json_data=payload,
            )
            if not response:
                return None

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            try:
                tag_data = json.loads(content)
                return tag_data.get("tags", [])
            except json.JSONDecodeError:
                return [t.strip() for t in content.split(",") if t.strip()]
        except Exception as e:
            logger.error(f"Failed to generate tags: {e}")
            return None

    async def _get_title(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """Generate a title for the conversation asynchronously."""
        try:
            task_model = await self.base_client._get_task_model()
            if not task_model:
                return None

            payload = {"model": task_model, "messages": messages, "stream": False}
            response = await self.base_client._make_request(
                "POST",
                "/api/v1/tasks/title/completions",
                json_data=payload,
            )
            if not response:
                return None

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            try:
                title_data = json.loads(content)
                return title_data.get("title", content.strip())
            except json.JSONDecodeError:
                return content.strip() if content else None
        except Exception as e:
            logger.error(f"Failed to generate title: {e}")
            return None

    async def _set_chat_tags(self, chat_id: str, tags: List[str]) -> None:
        if not tags:
            return
        try:
            existing_resp = await self.base_client._make_request(
                "GET", f"/api/v1/chats/{chat_id}/tags"
            )
            existing = set()
            if existing_resp:
                try:
                    existing = {
                        t.get("name") for t in existing_resp.json() if t.get("name")
                    }
                except Exception:
                    existing = set()

            for tag_name in tags:
                if tag_name in existing:
                    continue
                await self.base_client._make_request(
                    "POST",
                    f"/api/v1/chats/{chat_id}/tags",
                    json_data={"name": tag_name},
                )
        except Exception as e:
            logger.error(f"Failed to set tags for chat {chat_id}: {e}")

    async def _rename_chat(self, chat_id: str, new_title: str) -> bool:
        try:
            response = await self.base_client._make_request(
                "POST",
                f"/api/v1/chats/{chat_id}",
                json_data={"chat": {"title": new_title}},
            )
            return bool(response)
        except Exception as e:
            logger.error(f"Failed to rename chat {chat_id}: {e}")
            return False

    async def _get_folder_id_by_name(self, folder_name: str) -> Optional[str]:
        try:
            response = await self.base_client._make_request("GET", "/api/v1/folders/")
            if not response:
                return None
            for folder in response.json() or []:
                if folder.get("name") == folder_name:
                    return folder.get("id")
            return None
        except Exception as e:
            logger.error(f"Failed to lookup folder '{folder_name}': {e}")
            return None

    async def _create_folder(self, name: str) -> Optional[str]:
        try:
            response = await self.base_client._make_request(
                "POST", "/api/v1/folders/", json_data={"name": name}
            )
            if response:
                return response.json().get("id") or await self._get_folder_id_by_name(
                    name
                )
            return None
        except Exception as e:
            logger.error(f"Failed to create folder '{name}': {e}")
            return None

    async def _move_chat_to_folder(self, chat_id: str, folder_id: str) -> None:
        try:
            await self.base_client._make_request(
                "POST",
                f"/api/v1/chats/{chat_id}/folder",
                json_data={"folder_id": folder_id},
            )
        except Exception as e:
            logger.error(f"Failed to move chat {chat_id} to folder {folder_id}: {e}")

    async def _ensure_folder(self, chat_id: str, folder_name: str) -> None:
        folder_id = await self._get_folder_id_by_name(folder_name)
        if not folder_id:
            folder_id = await self._create_folder(folder_name)
        if folder_id:
            await self._move_chat_to_folder(chat_id, folder_id)
