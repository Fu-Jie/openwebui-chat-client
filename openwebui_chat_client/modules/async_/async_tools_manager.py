"""Async Tools Manager - Managing OpenWebUI server-side tools."""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from openwebui_chat_client.core.async_base_client import AsyncBaseClient

logger = logging.getLogger(__name__)


class AsyncToolsManager:
    """
    Async Tools Manager - Handles Python tools on the OpenWebUI server.
    Reference: /api/v1/tools
    """

    def __init__(self, base_client: "AsyncBaseClient"):
        self.base_client = base_client

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools accessible to the current user."""
        resp = await self.base_client._get_json_response("GET", "/api/v1/tools/")
        return resp if isinstance(resp, list) else []

    async def list_tools_with_access(self) -> List[Dict[str, Any]]:
        """List tools with explicit write-access flags."""
        resp = await self.base_client._get_json_response("GET", "/api/v1/tools/list")
        return resp if isinstance(resp, list) else []

    async def export_tools(self) -> List[Dict[str, Any]]:
        """Export all tools as full model objects including content and specs."""
        resp = await self.base_client._get_json_response("GET", "/api/v1/tools/export")
        return resp if isinstance(resp, list) else []

    async def create_tool(
        self,
        id: str,
        name: str,
        content: str,
        meta: Dict[str, Any],
        access_grants: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new tool from Python source code."""
        payload = {"id": id, "name": name, "content": content, "meta": meta}
        if access_grants is not None:
            payload["access_grants"] = access_grants

        return await self.base_client._get_json_response(
            "POST", "/api/v1/tools/create", json_data=payload
        )

    async def get_tool_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a tool by ID with write-access flag."""
        return await self.base_client._get_json_response(
            "GET", f"/api/v1/tools/id/{id}"
        )

    async def update_tool_by_id(
        self,
        id: str,
        name: str,
        content: str,
        meta: Dict[str, Any],
        access_grants: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update an existing tool's source code and metadata."""
        payload = {"id": id, "name": name, "content": content, "meta": meta}
        if access_grants is not None:
            payload["access_grants"] = access_grants

        return await self.base_client._get_json_response(
            "POST", f"/api/v1/tools/id/{id}/update", json_data=payload
        )

    async def update_tool_access(
        self, id: str, access_grants: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Update access grants for a tool."""
        payload = {"access_grants": access_grants}
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/tools/id/{id}/access/update", json_data=payload
        )

    async def delete_tool_by_id(self, id: str) -> bool:
        """Delete a tool by ID."""
        resp = await self.base_client._make_request(
            "DELETE", f"/api/v1/tools/id/{id}/delete"
        )
        return resp is not None and resp.status_code == 200

    # Valves management
    async def get_tool_valves(self, id: str) -> Dict[str, Any]:
        """Get global valve settings for a tool."""
        resp = await self.base_client._get_json_response(
            "GET", f"/api/v1/tools/id/{id}/valves"
        )
        return resp if isinstance(resp, dict) else {}

    async def update_tool_valves(
        self, id: str, valves: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update global valve settings for a tool."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/tools/id/{id}/valves/update", json_data=valves
        )

    async def get_user_valves(self, id: str) -> Dict[str, Any]:
        """Get current user's personal valve settings for a tool."""
        resp = await self.base_client._get_json_response(
            "GET", f"/api/v1/tools/id/{id}/valves/user"
        )
        return resp if isinstance(resp, dict) else {}

    async def update_user_valves(
        self, id: str, valves: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update current user's personal valve settings for a tool."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/tools/id/{id}/valves/user/update", json_data=valves
        )

    # Helper methods
    async def upsert_tool_from_file(
        self,
        file_path: str,
        tool_id: Optional[str] = None,
        access_grants: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Upsert a tool from a local Python file.
        Automatically extracts name from the filename if not provided.
        """
        if not os.path.exists(file_path):
            logger.error(f"Tool file not found: {file_path}")
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        base_name = os.path.basename(file_path)
        t_id = tool_id or os.path.splitext(base_name)[0].lower().replace("-", "_")
        name = t_id.replace("_", " ").title()

        # Try to find existing tool to get its meta or just update
        try:
            existing = await self.get_tool_by_id(t_id)
        except Exception:
            existing = None

        meta = {"description": f"Uploaded from {base_name}", "manifest": {}}
        if existing and "meta" in existing:
            meta = existing["meta"]

        if existing:
            logger.info(f"Updating existing tool: {t_id}")
            # If access_grants not explicitly provided, preserve existing if possible
            if access_grants is None and "access_grants" in existing:
                access_grants = existing.get("access_grants")
            return await self.update_tool_by_id(
                t_id, name, content, meta, access_grants
            )
        else:
            logger.info(f"Creating new tool: {t_id}")
            return await self.create_tool(t_id, name, content, meta, access_grants)

    async def diff_tools(self, local_dir: str) -> Dict[str, List[str]]:
        """
        Compare local tool files (.py) against remote tools.
        Returns a dictionary categorizing tools by their ID:
        {
            "local_only": [...],
            "remote_only": [...],
            "matching": [...]
        }
        """
        if not os.path.exists(local_dir):
            raise ValueError(f"Local directory does not exist: {local_dir}")

        local_files = [f for f in os.listdir(local_dir) if f.endswith(".py")]
        local_ids = {
            os.path.splitext(f)[0].lower().replace("-", "_"): os.path.join(local_dir, f)
            for f in local_files
        }

        remote_list = await self.list_tools()
        remote_ids = {f["id"]: f for f in remote_list} if remote_list else {}

        local_only = [i for i in local_ids.keys() if i not in remote_ids]
        remote_only = [i for i in remote_ids.keys() if i not in local_ids]
        matching = [i for i in local_ids.keys() if i in remote_ids]

        return {
            "local_only": local_only,
            "remote_only": remote_only,
            "matching": matching,
        }
