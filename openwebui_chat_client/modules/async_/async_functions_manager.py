"""Async Functions Manager - Managing OpenWebUI server-side plugins (Filters, Actions, Pipes)."""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import os

from openwebui_chat_client.models import Function

if TYPE_CHECKING:
    from openwebui_chat_client.core.async_base_client import AsyncBaseClient

logger = logging.getLogger(__name__)


class AsyncFunctionsManager:
    """
    Async Functions Manager - Handles Python plugins on the OpenWebUI server.
    Reference: /api/v1/functions
    """

    def __init__(self, base_client: "AsyncBaseClient"):
        self.base_client = base_client

    async def list_functions(self) -> List[Dict[str, Any]]:
        """List all functions (summary view)."""
        resp = await self.base_client._get_json_response("GET", "/api/v1/functions/")
        return resp if isinstance(resp, list) else []

    async def list_all_functions(self) -> List[Dict[str, Any]]:
        """List all functions with creator info (Admin only)."""
        resp = await self.base_client._get_json_response(
            "GET", "/api/v1/functions/list"
        )
        return resp if isinstance(resp, list) else []

    async def export_functions(
        self, include_valves: bool = False
    ) -> List[Dict[str, Any]]:
        """Export all functions including source code (Admin only)."""
        params = {"include_valves": str(include_valves).lower()}
        resp = await self.base_client._get_json_response(
            "GET", "/api/v1/functions/export", params=params
        )
        return resp if isinstance(resp, list) else []

    async def create_function(
        self, id: str, name: str, content: str, meta: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new function (Admin only)."""
        payload = {"id": id, "name": name, "content": content, "meta": meta}
        return await self.base_client._get_json_response(
            "POST", "/api/v1/functions/create", json_data=payload
        )

    async def get_function_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get function details including source code (Admin only)."""
        return await self.base_client._get_json_response(
            "GET", f"/api/v1/functions/id/{id}"
        )

    async def update_function_by_id(
        self, id: str, name: str, content: str, meta: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing function (Admin only)."""
        payload = {"id": id, "name": name, "content": content, "meta": meta}
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/update", json_data=payload
        )

    async def delete_function_by_id(self, id: str) -> bool:
        """Delete a function (Admin only)."""
        resp = await self.base_client._make_request(
            "DELETE", f"/api/v1/functions/id/{id}/delete"
        )
        return resp is not None and resp.status_code == 200

    async def toggle_function(self, id: str) -> Optional[Dict[str, Any]]:
        """Toggle function active state (Admin only)."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/toggle"
        )

    async def toggle_global_function(self, id: str) -> Optional[Dict[str, Any]]:
        """Toggle function global state (Admin only)."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/toggle/global"
        )

    # Valves management
    async def get_function_valves(self, id: str) -> Dict[str, Any]:
        """Get global valve settings (Admin only)."""
        resp = await self.base_client._get_json_response(
            "GET", f"/api/v1/functions/id/{id}/valves"
        )
        return resp if isinstance(resp, dict) else {}

    async def update_function_valves(
        self, id: str, valves: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update global valve settings (Admin only)."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/valves/update", json_data=valves
        )

    async def get_user_valves(self, id: str) -> Dict[str, Any]:
        """Get current user's personal valve settings."""
        resp = await self.base_client._get_json_response(
            "GET", f"/api/v1/functions/id/{id}/valves/user"
        )
        return resp if isinstance(resp, dict) else {}

    async def update_user_valves(
        self, id: str, valves: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update current user's personal valve settings."""
        return await self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/valves/user/update", json_data=valves
        )

    # Helper methods
    async def upsert_function_from_file(
        self, file_path: str, function_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Upsert a function from a local Python file.
        Automatically extracts name from the filename if not provided.
        """
        if not os.path.exists(file_path):
            logger.error(f"Function file not found: {file_path}")
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        base_name = os.path.basename(file_path)
        func_id = function_id or os.path.splitext(base_name)[0].lower().replace(
            "-", "_"
        )
        name = func_id.replace("_", " ").title()

        # Try to find existing function to get its meta or just update
        existing = await self.get_function_by_id(func_id)
        meta = (
            existing.get(
                "meta", {"description": f"Uploaded from {base_name}", "manifest": {}}
            )
            if existing
            else {"description": f"Uploaded from {base_name}", "manifest": {}}
        )

        if existing:
            logger.info(f"Updating existing function: {func_id}")
            return await self.update_function_by_id(func_id, name, content, meta)
        else:
            logger.info(f"Creating new function: {func_id}")
            return await self.create_function(func_id, name, content, meta)

    async def diff_functions(self, local_dir: str) -> Dict[str, List[str]]:
        """
        Compare local function files (.py) against remote functions.
        Returns a dictionary categorizing functions by their ID:
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

        remote_list = await self.list_functions()
        remote_ids = {f["id"]: f for f in remote_list} if remote_list else {}

        local_only = [i for i in local_ids.keys() if i not in remote_ids]
        remote_only = [i for i in remote_ids.keys() if i not in local_ids]
        matching = [i for i in local_ids.keys() if i in remote_ids]

        return {
            "local_only": local_only,
            "remote_only": remote_only,
            "matching": matching,
        }
