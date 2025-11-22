"""
Async Notes management module.
"""

import logging
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.async_base_client import AsyncBaseClient

logger = logging.getLogger(__name__)


class AsyncNotesManager:
    def __init__(self, base_client: "AsyncBaseClient") -> None:
        self.base_client = base_client

    async def get_notes(self) -> Optional[List[Dict[str, Any]]]:
        return await self.base_client._get_json_response("GET", "/api/v1/notes/")
