"""
Async Prompts management module.
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class AsyncPromptsManager:
    def __init__(self, base_client):
        self.base_client = base_client

    async def get_prompts(self) -> Optional[List[Dict[str, Any]]]:
        return await self.base_client._get_json_response("GET", "/api/v1/prompts/")
