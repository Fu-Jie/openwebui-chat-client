"""Async Chat Workflow Orchestrator - Official Open WebUI Flow Implementation."""

import logging
import time
import json
from typing import Any, Dict, List, Optional, AsyncGenerator

from .api import AsyncChatAPI
from openwebui_chat_client.modules.chat.payloads import ChatPayloads
from openwebui_chat_client.modules.chat.types import (
    MessageDict,
    ChatDict,
    ResponseDict,
    WorkflowResultDict,
    MetadataDict,
    ChatID,
    MessageID,
    SessionID,
)

logger = logging.getLogger(__name__)


class AsyncChatWorkflow:
    """Async Chat Workflow Orchestrator."""

    def __init__(self, chat_api: AsyncChatAPI):
        self.api = chat_api

    async def execute_full_turn(
        self,
        question: str,
        chat_id: Optional[ChatID] = None,
        model: Optional[str] = None,
        chat_title: Optional[str] = None,
        parent_message_id: Optional[MessageID] = None,
        session_id: Optional[SessionID] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        tool_ids: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Optional[WorkflowResultDict]:
        """Execute complete async chat turn following official Open WebUI workflow."""
        workflow_step = "initialization"

        try:
            # Step 0: Metadata & Chat Discovery
            workflow_step = "metadata_preparation"
            if not question or not model:
                logger.error("Question and model are required")
                return None

            if not chat_id and chat_title:
                # Discover existing chat by title
                for page in (1, 2):
                    chats = await self.api.list_chats(page=page)
                    if not chats:
                        break
                    for c in chats:
                        c_title = (
                            c.get("title")
                            if hasattr(c, "get")
                            else getattr(c, "title", None)
                        )
                        c_id = (
                            c.get("id") if hasattr(c, "get") else getattr(c, "id", None)
                        )
                        if c_title == chat_title and c_id:
                            chat_id = c_id
                            break
                    if chat_id:
                        break

            if not chat_id:
                # Create new chat
                chat_payload = ChatPayloads.build_chat_payload(
                    title=chat_title or "New Chat",
                    messages=[],
                    current_id="",
                    models=[model] if model else [],
                )
                chat_resp = await self.api.create_chat(chat_payload)
                if not chat_resp:
                    return None
                chat_id = chat_resp.get("id")

            # If we have a chat_id but no parent_id, try to fetch the latest for continuity
            if chat_id and not parent_message_id:
                details = await self.api.get_chat(chat_id)
                if details:
                    # Robust access to currentId
                    chat_data = details.get("chat", {})
                    history = chat_data.get("history", {})
                    parent_message_id = history.get("currentId")
                    logger.debug(
                        f"Auto-resolved parent_message_id: {parent_message_id}"
                    )

            # Build user message
            user_msg = ChatPayloads.build_user_message(
                content=question,
                model=model,
                parent_id=parent_message_id,
                files=files,
            )
            user_message_id = user_msg["id"]

            # Retrieve linear history context for completion parity
            history_context = []
            if chat_id and parent_message_id:
                history_context = await self._get_linear_history(
                    chat_id, parent_message_id
                )

            # Step 1: Completion
            workflow_step = "completion"
            completion_payload = ChatPayloads.build_completion_payload(
                model=model,
                messages=history_context + [user_msg],
                chat_id=chat_id,
                message_id=user_message_id,
                parent_message_id=parent_message_id,
                session_id=session_id or f"session_{int(time.time())}",
                stream=stream,
                files=files,
                tool_ids=tool_ids,
                **kwargs,
            )

            metadata = {
                "chat_id": chat_id,
                "message_id": user_message_id,
                "parent_message_id": parent_message_id,
                "session_id": completion_payload["session_id"],
                "files": files,
            }

            completion_resp = await self.api.completion(completion_payload)
            if not completion_resp:
                return None

            # Extract assistant message
            choices = completion_resp.get("choices", [])
            if not choices:
                return None
            assistant_message = choices[0].get("message", {})
            assistant_content = assistant_message.get("content", "")
            assistant_message_id = completion_resp.get("id", f"msg_{int(time.time())}")
            metadata["message_id"] = assistant_message_id

            # Step 2: Completed (Filters)
            workflow_step = "completed"
            completed_payload = ChatPayloads.build_completed_payload(
                chat_id=chat_id,
                message_id=metadata["message_id"],
                model=model,
                messages=[user_msg],
                session_id=metadata["session_id"],
                **kwargs,
            )
            await self.api.completed(completed_payload)

            # Step 3: Persist with History Merge (The CRITICAL Fix)
            workflow_step = "persist"
            all_messages = await self._get_existing_messages(chat_id)
            logger.debug(f"Merging history: {len(all_messages)} existing messages")

            new_ids = {user_msg["id"], assistant_message_id}
            all_messages = [m for m in all_messages if m.get("id") not in new_ids]

            assistant_msg = ChatPayloads.build_assistant_message(
                content=assistant_content,
                model=model,
                parent_id=user_message_id,
                msg_id=assistant_message_id,
            )

            current_messages = all_messages + [user_msg, assistant_msg]
            logger.debug(f"Final message count to persist: {len(current_messages)}")

            chat_object = ChatPayloads.build_chat_object(
                title=chat_title or "New Chat",
                messages=current_messages,
                current_id=assistant_msg["id"],
                models=[model],
            )

            persist_payload = {"chat": chat_object}
            final_state = await self.api.update_chat(chat_id, persist_payload)

            return {
                "success": True,
                "chat_id": chat_id,
                "metadata": metadata,
                "user_message": user_msg,
                "assistant_message": {
                    "id": metadata["message_id"],
                    "content": assistant_content,
                },
                "completion_response": completion_resp,
                "chat_state": final_state,
            }

        except Exception as e:
            logger.error(
                f"Async Workflow failed at '{workflow_step}': {e}", exc_info=True
            )
            return {
                "success": False,
                "error": str(e),
                "workflow_step_failed": workflow_step,
                "chat_id": chat_id,
            }

    async def _get_existing_messages(
        self, chat_id: Optional[ChatID]
    ) -> List[MessageDict]:
        """Helper to fetch and extract all existing messages from a chat asynchronously."""
        if not chat_id:
            return []
        details = await self.api.get_chat(chat_id)
        if not details:
            return []

        chat_data = (
            details.get("chat", {})
            if hasattr(details, "get")
            else getattr(details, "chat", {})
        )
        history = (
            chat_data.get("history", {})
            if hasattr(chat_data, "get")
            else getattr(chat_data, "history", {})
        )
        messages_dict = (
            history.get("messages", {})
            if hasattr(history, "get")
            else getattr(history, "messages", {})
        )

        return list(messages_dict.values()) if hasattr(messages_dict, "values") else []

    async def _get_linear_history(
        self, chat_id: Optional[ChatID], parent_id: Optional[MessageID]
    ) -> List[MessageDict]:
        """Reconstruct linear conversation history up to parent_id."""
        if not chat_id or not parent_id:
            return []
        messages = await self._get_existing_messages(chat_id)
        if not messages:
            return []

        msg_map = {m.get("id"): m for m in messages if m.get("id")}
        linear = []
        curr = parent_id
        while curr and curr in msg_map:
            m = msg_map[curr]
            linear.append(m)
            curr = m.get("parentId")

        return list(reversed(linear))

    async def regenerate_message(
        self,
        chat_id: ChatID,
        parent_message_id: MessageID,
        model: Optional[str] = None,
        **kwargs,
    ) -> Optional[WorkflowResultDict]:
        """Regenerate assistant response asynchronously."""
        details = await self.api.get_chat(chat_id)
        if not details:
            return None

        messages = await self._get_existing_messages(chat_id)
        messages_dict = {m.get("id"): m for m in messages}
        parent_msg = messages_dict.get(parent_message_id)
        if not parent_msg:
            return None

        content = parent_msg.get("content")
        grandparent_id = parent_msg.get("parentId")

        return await self.execute_full_turn(
            question=content,
            chat_id=chat_id,
            model=model,
            parent_message_id=grandparent_id,
            **kwargs,
        )

    async def edit_message(
        self,
        chat_id: ChatID,
        message_id: MessageID,
        new_content: str,
        model: Optional[str] = None,
        **kwargs,
    ) -> Optional[WorkflowResultDict]:
        """Edit a user message and trigger new branch asynchronously."""
        details = await self.api.get_chat(chat_id)
        if not details:
            return None

        messages = await self._get_existing_messages(chat_id)
        messages_dict = {m.get("id"): m for m in messages}
        target_msg = messages_dict.get(message_id)
        if not target_msg:
            return None

        parent_id = target_msg.get("parentId")
        return await self.execute_full_turn(
            question=new_content,
            chat_id=chat_id,
            model=model,
            parent_message_id=parent_id,
            **kwargs,
        )
