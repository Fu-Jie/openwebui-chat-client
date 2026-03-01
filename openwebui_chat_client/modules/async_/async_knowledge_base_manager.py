"""Async Knowledge Base management module."""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from openwebui_chat_client.core.async_base_client import AsyncBaseClient

from openwebui_chat_client.models import KnowledgeResponse

logger = logging.getLogger(__name__)


class AsyncKnowledgeBaseManager:
    """
    Async Knowledge Base Manager - Handles KB creation, file association, and vector store indexing.
    Reference: /api/v1/knowledge
    """

    def __init__(self, base_client: "AsyncBaseClient") -> None:
        self.base_client = base_client

    async def get_knowledge_base_by_name(
        self, name: str
    ) -> Optional[KnowledgeResponse]:
        """Utility method to find a knowledge base by exact name."""
        response = await self.base_client._get_json_response(
            "GET", "/api/v1/knowledge/"
        )
        if response and "items" in response:
            for kb in response["items"]:
                if kb.get("name") == name:
                    return KnowledgeResponse.model_validate(kb)
        return None

    async def list_knowledge_bases(self, page: int = 1) -> Dict[str, Any]:
        """List knowledge bases (paginated)."""
        params = {"page": page}
        resp = await self.base_client._get_json_response(
            "GET", "/api/v1/knowledge/", params=params
        )
        return resp if isinstance(resp, dict) else {}

    async def search_knowledge_bases(
        self,
        query: Optional[str] = None,
        view_option: Optional[str] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search KBs by name, description, or owner."""
        params = {"page": page}
        if query:
            params["query"] = query
        if view_option:
            params["view_option"] = view_option

        resp = await self.base_client._get_json_response(
            "GET", "/api/v1/knowledge/search", params=params
        )
        return resp if isinstance(resp, dict) else {}

    async def search_files(
        self, query: Optional[str] = None, page: int = 1
    ) -> Dict[str, Any]:
        """Search files across all accessible knowledge bases."""
        params = {"page": page}
        if query:
            params["query"] = query

        resp = await self.base_client._get_json_response(
            "GET", "/api/v1/knowledge/search/files", params=params
        )
        return resp if isinstance(resp, dict) else {}

    async def create_knowledge_base(
        self,
        name: str,
        description: str,
        access_grants: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[KnowledgeResponse]:
        """Create a new knowledge base."""
        payload = {"name": name, "description": description}
        if access_grants is not None:
            payload["access_grants"] = access_grants

        data = await self.base_client._get_json_response(
            "POST", "/api/v1/knowledge/create", json_data=payload
        )
        if data:
            return KnowledgeResponse.model_validate(data)
        return None

    async def reindex_all_knowledge_bases(self) -> bool:
        """Reindex all files in every knowledge base (Admin only)."""
        resp = await self.base_client._make_request("POST", "/api/v1/knowledge/reindex")
        return resp is not None and resp.status_code == 200

    async def reindex_all_metadata(self) -> Optional[Dict[str, Any]]:
        """Re-embed metadata for all knowledge bases (Admin only)."""
        return await self.base_client._get_json_response(
            "POST", "/api/v1/knowledge/metadata/reindex"
        )

    async def get_knowledge_base_details(
        self, kb_id: str
    ) -> Optional[KnowledgeResponse]:
        """Retrieve a knowledge base by ID including linked files."""
        data = await self.base_client._get_json_response(
            "GET", f"/api/v1/knowledge/{kb_id}"
        )
        if data:
            return KnowledgeResponse.model_validate(data)
        return None

    async def update_knowledge_base(
        self,
        kb_id: str,
        name: str,
        description: str,
        access_grants: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[KnowledgeResponse]:
        """Update name, description, and/or access grants."""
        payload = {"name": name, "description": description}
        if access_grants is not None:
            payload["access_grants"] = access_grants

        data = await self.base_client._get_json_response(
            "POST", f"/api/v1/knowledge/{kb_id}/update", json_data=payload
        )
        if data:
            return KnowledgeResponse.model_validate(data)
        return None

    async def update_knowledge_base_access(
        self, kb_id: str, access_grants: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Replace access grants for a knowledge base."""
        payload = {"access_grants": access_grants}
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/knowledge/{kb_id}/access/update", json_data=payload
        )

    async def list_knowledge_base_files(
        self,
        kb_id: str,
        query: Optional[str] = None,
        view_option: Optional[str] = None,
        order_by: Optional[str] = None,
        direction: Optional[str] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        """List files linked to a specific knowledge base."""
        params = {"page": page}
        if query:
            params["query"] = query
        if view_option:
            params["view_option"] = view_option
        if order_by:
            params["order_by"] = order_by
        if direction:
            params["direction"] = direction

        resp = await self.base_client._get_json_response(
            "GET", f"/api/v1/knowledge/{kb_id}/files", params=params
        )
        return resp if isinstance(resp, dict) else {}

    async def add_file_to_knowledge_base(
        self, kb_id: str, file_id: str
    ) -> Optional[Dict[str, Any]]:
        """Add an already-uploaded file to a knowledge base."""
        payload = {"file_id": file_id}
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/knowledge/{kb_id}/file/add", json_data=payload
        )

    async def update_file_in_knowledge_base(
        self, kb_id: str, file_id: str
    ) -> Optional[Dict[str, Any]]:
        """Re-embed a file already linked to a knowledge base."""
        payload = {"file_id": file_id}
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/knowledge/{kb_id}/file/update", json_data=payload
        )

    async def remove_file_from_knowledge_base(
        self, kb_id: str, file_id: str, delete_file: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Remove a file from a knowledge base."""
        payload = {"file_id": file_id}
        params = {"delete_file": str(delete_file).lower()}
        return await self.base_client._get_json_response(
            "POST",
            f"/api/v1/knowledge/{kb_id}/file/remove",
            json_data=payload,
            params=params,
        )

    async def delete_knowledge_base(self, kb_id: str) -> bool:
        """Permanently delete a knowledge base."""
        resp = await self.base_client._make_request(
            "DELETE", f"/api/v1/knowledge/{kb_id}/delete"
        )
        return resp is not None and resp.status_code == 200

    async def reset_knowledge_base(self, kb_id: str) -> Optional[Dict[str, Any]]:
        """Clear all file associations and delete vector collection."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/knowledge/{kb_id}/reset"
        )

    async def batch_add_files_to_knowledge_base(
        self, kb_id: str, file_ids: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Add multiple files to a knowledge base in a batch."""
        payload = [{"file_id": fid} for fid in file_ids]
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/knowledge/{kb_id}/files/batch/add", json_data=payload
        )
