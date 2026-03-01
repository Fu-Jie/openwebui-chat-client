"""
Async Notes management module.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..core.async_base_client import AsyncBaseClient
from openwebui_chat_client.models import NoteResponse

logger = logging.getLogger(__name__)


class AsyncNotesManager:
    def __init__(self, base_client: "AsyncBaseClient") -> None:
        self.base_client = base_client

    async def get_notes(self) -> Optional[List[NoteResponse]]:
        """Get all notes for the current user."""
        notes = await self.base_client._get_json_response("GET", "/api/v1/notes/")
        if isinstance(notes, list):
            return [NoteResponse.model_validate(n) for n in notes]
        return None
