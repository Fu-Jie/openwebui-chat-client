"""Functions Manager - Managing OpenWebUI server-side plugins (Filters, Actions, Pipes)."""

import logging
import os
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from openwebui_chat_client.models import Function

if TYPE_CHECKING:
    from openwebui_chat_client.core.base_client import BaseClient

logger = logging.getLogger(__name__)


class FunctionsManager:
    """
    Functions Manager - Handles Python plugins on the OpenWebUI server.
    Reference: /api/v1/functions
    """

    def __init__(self, base_client: "BaseClient"):
        self.base_client = base_client

    def get_functions(self) -> Optional[List[Function]]:
        """Get all available functions as Pydantic models."""
        resp = self.list_functions()
        if resp:
            return [Function.model_validate(f) for f in resp]
        return []

    def get_actions(self) -> List[Function]:
        """Get only functions of type 'action'."""
        functions = self.get_functions()
        if not functions:
            return []
        return [f for f in functions if f.is_action]

    def list_functions(self) -> List[Dict[str, Any]]:
        """List all functions (summary view)."""
        resp = self.base_client._get_json_response("GET", "/api/v1/functions/")
        return resp if isinstance(resp, list) else []

    def list_all_functions(self) -> List[Dict[str, Any]]:
        """List all functions with creator info (Admin only)."""
        resp = self.base_client._get_json_response(
            "GET", "/api/v1/functions/list"
        )
        return resp if isinstance(resp, list) else []

    def export_functions(
        self, include_valves: bool = False
    ) -> List[Dict[str, Any]]:
        """Export all functions including source code (Admin only)."""
        params = {"include_valves": str(include_valves).lower()}
        resp = self.base_client._get_json_response(
            "GET", "/api/v1/functions/export", params=params
        )
        return resp if isinstance(resp, list) else []

    def create_function(
        self, id: str, name: str, content: str, meta: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new function (Admin only)."""
        payload = {"id": id, "name": name, "content": content, "meta": meta}
        return self.base_client._get_json_response(
            "POST", "/api/v1/functions/create", json_data=payload
        )

    def get_function_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get function details including source code (Admin only)."""
        return self.base_client._get_json_response(
            "GET", f"/api/v1/functions/id/{id}"
        )

    def update_function_by_id(
        self, id: str, name: str, content: str, meta: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing function (Admin only)."""
        payload = {"id": id, "name": name, "content": content, "meta": meta}
        return self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/update", json_data=payload
        )

    def delete_function_by_id(self, id: str) -> bool:
        """Delete a function (Admin only)."""
        resp = self.base_client._make_request(
            "DELETE", f"/api/v1/functions/id/{id}/delete"
        )
        return resp is not None and resp.status_code == 200

    def toggle_function(self, id: str) -> Optional[Dict[str, Any]]:
        """Toggle function active state (Admin only)."""
        return self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/toggle"
        )

    def toggle_global_function(self, id: str) -> Optional[Dict[str, Any]]:
        """Toggle function global state (Admin only)."""
        return self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/toggle/global"
        )

    # Valves management
    def get_function_valves(self, id: str) -> Dict[str, Any]:
        """Get global valve settings (Admin only)."""
        resp = self.base_client._get_json_response(
            "GET", f"/api/v1/functions/id/{id}/valves"
        )
        return resp if isinstance(resp, dict) else {}

    def update_function_valves(
        self, id: str, valves: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update global valve settings (Admin only)."""
        return self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/valves/update", json_data=valves
        )

    def get_user_valves(self, id: str) -> Dict[str, Any]:
        """Get current user's personal valve settings."""
        resp = self.base_client._get_json_response(
            "GET", f"/api/v1/functions/id/{id}/valves/user"
        )
        return resp if isinstance(resp, dict) else {}

    def update_user_valves(
        self, id: str, valves: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update current user's personal valve settings."""
        return self.base_client._get_json_response(
            "POST", f"/api/v1/functions/id/{id}/valves/user/update", json_data=valves
        )
