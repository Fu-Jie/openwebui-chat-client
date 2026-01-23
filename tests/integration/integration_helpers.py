"""
Shared helpers for integration tests.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv


def ensure_env_loaded() -> bool:
    """Load .env and return whether required env vars are present."""
    load_dotenv()
    return bool(os.getenv("OUI_BASE_URL") and os.getenv("OUI_AUTH_TOKEN"))


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get env var with optional default."""
    return os.getenv(name, default)


def normalize_chat_response(result: Any) -> Dict[str, Optional[str]]:
    """Normalize chat result to a dict with response/chat_id/message_id."""
    if not result:
        return {"response": None, "chat_id": None, "message_id": None}

    if isinstance(result, dict):
        return {
            "response": result.get("response"),
            "chat_id": result.get("chat_id"),
            "message_id": result.get("message_id"),
        }

    return {
        "response": getattr(result, "response", None),
        "chat_id": getattr(result, "chat_id", None),
        "message_id": getattr(result, "message_id", None),
    }
