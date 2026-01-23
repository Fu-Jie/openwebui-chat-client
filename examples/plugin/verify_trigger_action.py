"""
Example script to verify the trigger_action functionality.

This script demonstrates how to use the trigger_action method to invoke
a backend action in Open WebUI.

Usage:
    export OUI_BASE_URL="http://localhost:3003"
    export OUI_AUTH_TOKEN="your-token"
    export OUI_DEFAULT_MODEL="gpt-4"
    python examples/plugin/verify_trigger_action.py
"""

import os
import sys
import logging
import json
import base64
from datetime import datetime

# Add project root to sys.path to ensure we import the local package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openwebui_chat_client import OpenWebUIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv

load_dotenv()


def get_user_id_from_token(token):
    try:
        # JWT is header.payload.signature
        if not token or len(token.split(".")) < 2:
            return None
        payload_part = token.split(".")[1]
        # Add padding if needed
        payload_part += "=" * (-len(payload_part) % 4)
        decoded = base64.b64decode(payload_part)
        payload = json.loads(decoded)
        return payload.get("id")
    except Exception:
        return None


def main():
    # 1. Initialize client
    base_url = os.getenv("OUI_BASE_URL", "http://localhost:3003")
    token = os.getenv("OUI_AUTH_TOKEN")
    default_model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4")

    if not token:
        logger.error("Please set OUI_AUTH_TOKEN environment variable")
        return

    client = OpenWebUIClient(
        base_url=base_url, token=token, default_model_id=default_model
    )
    logger.info(f"Connected to Open WebUI at {base_url}")

    # Get User Info
    user = None
    try:
        logger.info("Fetching current user info from /api/v1/auths/...")
        response = client.session.get(
            f"{client.base_url}/api/v1/auths/", headers=client.json_headers
        )
        if response.status_code == 200:
            user = response.json()
            logger.info(
                f"Successfully retrieved current user: {user.get('name')} ({user.get('id')})"
            )
        else:
            logger.warning(
                f"Failed to get current user: {response.status_code} {response.text}"
            )
    except Exception as e:
        logger.error(f"Error fetching current user: {e}")

    if not user:
        # Fallback to token decoding if auths endpoint fails
        user_id = get_user_id_from_token(token)
        if user_id:
            # Try to fetch by ID if we have it (might fail if 403)
            if hasattr(client, "user_manager"):
                try:
                    user = client.user_manager.get_user_by_id(user_id)
                except Exception:
                    pass
            if not user:
                user = {"id": user_id, "role": "user"}

    if user:
        logger.info(f"Retrieved user info for: {user.get('name', 'Unknown')}")
    else:
        logger.warning(
            "Could not retrieve user info. Action might fail if it requires user data."
        )

    # 2. Create a new chat and generate a message
    chat_title = f"Plugin Action Test {datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    question = (
        "请基于以下主题生成一段较长的中文说明，用于触发思维导图插件。"
        "主题：开源项目的贡献流程与代码评审最佳实践。"
        "要求：至少包含背景介绍、贡献步骤、代码评审要点、常见问题与建议，"
        "并使用分段叙述，字数不少于300字。"
    )
    logger.info(f"Creating chat: {chat_title}")

    chat_result = client.chat(
        question=question,
        chat_title=chat_title,
        model_id=default_model,
    )

    if not chat_result:
        logger.error("Failed to create chat or generate message")
        return

    chat_id = client.chat_id or chat_result.get("chat_id") or chat_result.get("id")
    if not chat_id:
        chats = client.list_chats()
        chat_id = chats[0]["id"] if chats else None

    if not chat_id:
        logger.error("Could not determine chat ID after creation")
        return

    logger.info(f"Using Chat ID: {chat_id}")

    # 3. Resolve message ID (prefer latest user message)
    message_id = chat_result.get("message_id")
    if not message_id:
        message_id = chat_result.get("message", {}).get("id")

    logger.info(f"Fetching details for chat {chat_id}...")
    chat_details = client.get_chat(chat_id)

    if not chat_details:
        logger.error("Failed to retrieve chat details")
        return

    # Extract messages
    try:
        messages = chat_details.get("chat", {}).get("history", {}).get("messages", {})
        if not messages:
            logger.error("Chat has no messages")
            return

        # Prefer a valid user message (non-empty content)
        sorted_messages = sorted(
            messages.values(), key=lambda x: x.get("timestamp", 0), reverse=True
        )

        target_message = None
        if message_id and message_id in messages:
            candidate = messages[message_id]
            if candidate.get("role") == "user" and candidate.get("content"):
                target_message = candidate

        if not target_message:
            for msg in sorted_messages:
                if msg.get("role") == "user" and msg.get("content"):
                    target_message = msg
                    break

        if not target_message:
            logger.error("No suitable user message found in chat")
            return

        message_id = target_message["id"]
        logger.info(
            f"Using Message ID: {message_id} (Role: {target_message.get('role')})"
        )

    except Exception as e:
        logger.error(f"Error parsing chat details: {e}")
        return

    # 4. Trigger Action (use payload structure from web UI)
    action_id = "smart_mind_map"
    logger.info(
        "Target admin action URL: http://localhost:3003/admin/functions/edit?id=smart_mind_map"
    )
    logger.info(f"Triggering action '{action_id}'...")

    import uuid
    import requests

    # Build messages array for payload
    sorted_messages_asc = sorted(messages.values(), key=lambda x: x.get("timestamp", 0))
    payload_messages = []
    for msg in sorted_messages_asc:
        if msg.get("role") not in ["user", "assistant"]:
            continue
        content = msg.get("content")
        if not content:
            continue
        payload_messages.append(
            {
                "id": msg.get("id"),
                "role": msg.get("role"),
                "content": content,
                "timestamp": msg.get("timestamp"),
                "sources": msg.get("sources", []),
            }
        )

    if not payload_messages:
        logger.error("No valid messages found to send to action endpoint")
        return

    latest_user_message = next(
        (m for m in reversed(payload_messages) if m.get("role") == "user"), None
    )
    latest_assistant_message = next(
        (m for m in reversed(payload_messages) if m.get("role") == "assistant"), None
    )

    target_id = (
        latest_assistant_message.get("id")
        if latest_assistant_message
        else (latest_user_message.get("id") if latest_user_message else message_id)
    )

    model_id = chat_details.get("chat", {}).get("models", [default_model])[0]
    model_item = chat_details.get("chat", {}).get("model_item")
    if not model_item:
        model_item = {"id": model_id, "name": model_id}

    payload = {
        "model": model_id,
        "messages": payload_messages,
        "model_item": model_item,
        "chat_id": chat_id,
        "session_id": str(uuid.uuid4()),
        "id": target_id,
    }

    try:
        result = client.trigger_action(
            action_id=action_id,
            chat_id=chat_id,
            message_id=target_id,
            params=payload,
        )
        if result:
            logger.info("✅ Action triggered successfully!")
            logger.info(f"Result: {result}")
        else:
            logger.error("❌ Failed to trigger action: empty result")
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
