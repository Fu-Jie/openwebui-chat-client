"""Tools Manager - Managing external tools/functions for OpenWebUI."""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from openwebui_chat_client.core.base_client import BaseClient

logger = logging.getLogger(__name__)


class ToolsManager:
    """
    Tools Manager - Handles external tools available to models.
    Reference: /api/v1/tools
    """

    def __init__(self, base_client: "BaseClient"):
        self.base_client = base_client

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        resp = self.base_client._get_json_response("GET", "/api/v1/tools/")
        return resp if isinstance(resp, list) else []

    def get_tool_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get tool details."""
        return self.base_client._get_json_response("GET", f"/api/v1/tools/id/{id}")

    def create_tool(
        self, id: str, name: str, content: str, meta: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new tool."""
        payload = {"id": id, "name": name, "content": content, "meta": meta}
        return self.base_client._get_json_response(
            "POST", "/api/v1/tools/create", json_data=payload
        )

    def update_tool_by_id(
        self, id: str, name: str, content: str, meta: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing tool."""
        payload = {"id": id, "name": name, "content": content, "meta": meta}
        return self.base_client._get_json_response(
            "POST", f"/api/v1/tools/id/{id}/update", json_data=payload
        )

    def delete_tool_by_id(self, id: str) -> bool:
        """Delete a tool."""
        resp = self.base_client._make_request(
            "DELETE", f"/api/v1/tools/id/{id}/delete"
        )
        return resp is not None and resp.status_code == 200

    def export_tools(self) -> List[Dict[str, Any]]:
        """Export all tools."""
        resp = self.base_client._get_json_response("GET", "/api/v1/tools/export")
        return resp if isinstance(resp, list) else []
