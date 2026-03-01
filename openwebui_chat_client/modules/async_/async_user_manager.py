"""
Async User management module for OpenWebUI Chat Client.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..core.async_base_client import AsyncBaseClient

from openwebui_chat_client.models import UserResponse

logger = logging.getLogger(__name__)


class AsyncUserManager:
    """
    Handles async user management operations for the OpenWebUI client.
    """

    def __init__(self, base_client: "AsyncBaseClient") -> None:
        self.base_client = base_client

    async def get_users(
        self, skip: int = 0, limit: int = 50
    ) -> Optional[List[UserResponse]]:
        """Get a list of all users."""
        users = await self.base_client._get_json_response(
            "GET", "/api/v1/users/", params={"skip": skip, "limit": limit}
        )
        if isinstance(users, list):
            return [UserResponse.model_validate(u) for u in users]
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get a specific user by their ID."""
        user_data = await self.base_client._get_json_response(
            "GET", f"/api/v1/users/{user_id}"
        )
        if user_data:
            return UserResponse.model_validate(user_data)
        return None

    async def update_user_role(self, user_id: str, role: str) -> bool:
        """Update a user's role."""
        if role not in ["admin", "user"]:
            logger.error(f"Invalid role '{role}'. Must be 'admin' or 'user'.")
            return False

        response = await self.base_client._make_request(
            "POST", f"/api/v1/users/{user_id}/update/role", json_data={"role": role}
        )
        return response is not None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        response = await self.base_client._make_request(
            "DELETE", f"/api/v1/users/{user_id}"
        )
        return response is not None
