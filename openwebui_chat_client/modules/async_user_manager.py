"""
Async User management module for OpenWebUI Chat Client.
"""

import logging
import httpx
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class AsyncUserManager:
    """
    Handles async user management operations for the OpenWebUI client.
    """

    def __init__(self, base_client):
        self.base_client = base_client

    async def get_users(self, skip: int = 0, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Get a list of all users."""
        return await self.base_client._get_json_response(
            "GET",
            "/api/v1/users/",
            params={"skip": skip, "limit": limit}
        )

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific user by their ID."""
        return await self.base_client._get_json_response(
            "GET",
            f"/api/v1/users/{user_id}"
        )

    async def update_user_role(self, user_id: str, role: str) -> bool:
        """Update a user's role."""
        if role not in ["admin", "user"]:
            logger.error(f"Invalid role '{role}'. Must be 'admin' or 'user'.")
            return False

        response = await self.base_client._make_request(
            "POST",
            f"/api/v1/users/{user_id}/update/role",
            json_data={"role": role}
        )
        return response is not None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        response = await self.base_client._make_request(
            "DELETE",
            f"/api/v1/users/{user_id}"
        )
        return response is not None
