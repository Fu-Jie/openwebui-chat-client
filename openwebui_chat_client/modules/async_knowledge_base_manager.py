"""
Asynchronous knowledge base management module for OpenWebUI Chat Client.
Handles all async knowledge base operations including CRUD and file management.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class AsyncKnowledgeBaseManager:
    """
    Handles all asynchronous knowledge base operations for the OpenWebUI client.
    """

    def __init__(self, base_client):
        """
        Initialize the async knowledge base manager.

        Args:
            base_client: The async base client instance for making API requests.
        """
        self.base_client = base_client

    async def list_knowledge_bases(self) -> Optional[List[Dict[str, Any]]]:
        """Asynchronously list all knowledge bases."""
        logger.info("Async listing all knowledge bases...")
        return await self.base_client._get_json_response("GET", "/api/v1/knowledge/list")

    async def get_knowledge_base_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Asynchronously get a knowledge base by its name."""
        logger.info(f"Async searching for knowledge base '{name}'...")
        kbs = await self.list_knowledge_bases()
        if kbs:
            for kb in kbs:
                if kb.get("name") == name:
                    logger.info("Found knowledge base.")
                    return kb
        logger.info(f"Knowledge base '{name}' not found.")
        return None

    async def create_knowledge_base(
        self, name: str, description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Asynchronously create a new knowledge base."""
        logger.info(f"Async creating knowledge base '{name}'...")
        payload = {"name": name, "description": description}
        return await self.base_client._get_json_response(
            "POST", "/api/v1/knowledge/create", json_data=payload
        )

    async def delete_knowledge_base(self, kb_id: str) -> bool:
        """Asynchronously deletes a knowledge base by its ID."""
        logger.info(f"Async deleting knowledge base '{kb_id}'...")
        response = await self.base_client._make_request(
            "DELETE", f"/api/v1/knowledge/{kb_id}/delete"
        )
        return response is not None and response.status_code == 200

    async def delete_all_knowledge_bases(self) -> Tuple[int, int]:
        """Asynchronously deletes all knowledge bases for the current user."""
        logger.info("Async bulk deleting all knowledge bases...")
        kbs = await self.list_knowledge_bases()
        if not kbs:
            logger.info("No knowledge bases found to delete.")
            return 0, 0

        tasks = [self.delete_knowledge_base(kb["id"]) for kb in kbs if kb.get("id")]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful

        logger.info(f"Async bulk delete completed: {successful} successful, {failed} failed.")
        return successful, failed

    # Note: add_file_to_knowledge_base and other methods involving file uploads
    # will depend on an async file manager, which will be created next.
    # I will add placeholder methods for now.

    async def add_file_to_knowledge_base(
        self, file_path: str, knowledge_base_name: str
    ) -> bool:
        """
        Asynchronously add a file to a knowledge base.
        Depends on an async file manager.
        """
        logger.warning("add_file_to_knowledge_base is not fully implemented yet.")
        # 1. Get/Create KB
        # 2. Upload file via an async file manager
        # 3. Add file to KB
        return False
