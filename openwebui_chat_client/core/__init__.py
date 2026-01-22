"""
Core module for OpenWebUI Chat Client.
Contains base client and manager infrastructure.
"""

from openwebui_chat_client.core.base_client import BaseClient
from openwebui_chat_client.core.base_manager import BaseManager

__all__ = [
    "BaseClient",
    "BaseManager",
]
