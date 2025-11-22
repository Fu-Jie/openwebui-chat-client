"""
Async Knowledge Base management module.
"""

import logging
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.async_base_client import AsyncBaseClient

logger = logging.getLogger(__name__)


class AsyncKnowledgeBaseManager:
    def __init__(self, base_client: "AsyncBaseClient") -> None:
        self.base_client = base_client

    async def get_knowledge_base_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        response = await self.base_client._make_request("GET", "/api/v1/knowledge/")
        if response:
            kbs = response.json()
            for kb in kbs:
                if kb.get("name") == name:
                    return kb
        return None

    async def get_knowledge_base_details(self, kb_id: str) -> Optional[Dict[str, Any]]:
        return await self.base_client._get_json_response("GET", f"/api/v1/knowledge/{kb_id}")
