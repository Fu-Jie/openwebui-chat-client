"""
Chat actions for OpenWebUI Chat Client.
"""

import logging
import urllib.parse
import uuid
from typing import Any, Dict, Optional, List

from openwebui_chat_client.models import ActionResult

logger = logging.getLogger(__name__)


class ChatActions:
    """
    Handler for action execution.
    Delegated by ChatManager.
    """

    def __init__(self, manager):
        self.manager = manager
        self.client = manager.base_client

    def trigger_action(
        self,
        action_id: str,
        chat_id: str,
        message_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[ActionResult]:
        """
        Trigger an action and synchronize the result based on format.
        - Dict with 'embeds' -> Sync to message embeds.
        - HTML String -> Append to message content (Artifacts mode).
        """
        logger.info(f"Triggering action '{action_id}' for message {message_id}...")

        # 1. Prepare Payload
        payload = {"chat_id": chat_id, "id": message_id, "message_id": message_id}
        if params:
            payload.update(params)

        if "session_id" not in payload:
            payload["session_id"] = str(uuid.uuid4())
        
        if "model" not in payload:
            payload["model"] = getattr(self.client, "model_id", None) or getattr(
                self.client, "default_model_id", "gpt-4o"
            )

        if "messages" not in payload:
            chat_details = self.manager.get_chat(chat_id)
            if chat_details and chat_details.chat and chat_details.chat.history:
                msgs_dict = chat_details.chat.history.messages
                payload["messages"] = [m.model_dump() for m in msgs_dict.values()]

        # 2. Execute Action
        encoded_action_id = urllib.parse.quote(action_id)
        url = f"{self.client.base_url}/api/chat/actions/{encoded_action_id}"

        try:
            response = self.client.session.post(
                url, headers=self.client.json_headers, json=payload
            )
            response.raise_for_status()
            
            is_json = "application/json" in response.headers.get("Content-Type", "")
            raw_result = response.json() if is_json else response.text
            
            # --- Post-processing: Strategy Selection ---
            sync_updates = {}

            # Case A: Embeds Format (Dictionary)
            if isinstance(raw_result, dict):
                # Check for standard OpenWebUI event structure
                if raw_result.get("type") == "embeds":
                    sync_updates["embeds"] = raw_result.get("data", {}).get("embeds", [])
                # Check for direct embeds list
                elif "embeds" in raw_result:
                    sync_updates["embeds"] = raw_result["embeds"]
                # Fallback for general content updates
                elif "content" in raw_result:
                    sync_updates["content"] = raw_result["content"]

            # Case B: Artifacts Mode (HTML String)
            elif isinstance(raw_result, str) and ("<html" in raw_result.lower() or "<div" in raw_result.lower()):
                logger.info(f"Captured HTML result. Applying Artifacts mode (append to content).")
                sync_updates["append_content"] = f"\n\n```html\n{raw_result}\n```"

            if sync_updates:
                self._perform_surgical_sync(chat_id, message_id, sync_updates)

            return ActionResult.from_dict(raw_result) if isinstance(raw_result, dict) else ActionResult(data=raw_result)

        except Exception as e:
            logger.error(f"Failed to trigger action '{action_id}': {e}")
            return None

    def _perform_surgical_sync(self, chat_id: str, message_id: str, updates: Dict[str, Any]):
        """Precisely sync embeds or content to the specific message."""
        try:
            latest_data = self.client._get_json_response("GET", f"/api/v1/chats/{chat_id}")
            if not latest_data: return

            chat_obj = latest_data.get("chat", {})
            history = chat_obj.get("history", {})
            messages = history.get("messages", {})
            if not messages: return

            # Work with messages as a dict for easy modification
            messages_dict = {m.get("id"): m for m in messages} if isinstance(messages, list) else messages.copy()

            if message_id in messages_dict:
                msg = messages_dict[message_id]
                has_changes = False

                # Apply Embeds
                if "embeds" in updates:
                    existing_embeds = msg.get("embeds") or []
                    # Append new embeds
                    msg["embeds"] = existing_embeds + updates["embeds"]
                    has_changes = True

                # Apply Artifacts (Append to Content)
                if "append_content" in updates:
                    suffix = updates["append_content"]
                    if suffix not in (msg.get("content") or ""):
                        msg["content"] = (msg.get("content") or "") + suffix
                        has_changes = True
                
                # Apply direct Content Update
                elif "content" in updates:
                    msg["content"] = updates["content"]
                    has_changes = True

                if has_changes:
                    messages_dict[message_id] = msg
                    update_payload = {
                        "chat": {
                            **chat_obj,
                            "title": latest_data.get("title") or chat_obj.get("title"),
                            "history": {**history, "messages": messages_dict}
                        }
                    }
                    self.client.session.post(
                        f"{self.client.base_url}/api/v1/chats/{chat_id}",
                        headers=self.client.json_headers,
                        json=update_payload
                    ).raise_for_status()
                    logger.info(f"✅ Action results synchronized to server (Mode: {'Embeds' if 'embeds' in updates else 'Artifacts'}).")
        except Exception as e:
            logger.warning(f"Surgical sync failed: {e}")
