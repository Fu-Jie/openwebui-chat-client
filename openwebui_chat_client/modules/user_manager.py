"""
User management module for OpenWebUI Chat Client.
Handles user administration operations including listing, updating roles, and deleting users.
"""

import logging
import requests
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.base_client import BaseClient

logger = logging.getLogger(__name__)


class UserManager:
    """
    Handles user management operations for the OpenWebUI client.

    This class manages:
    - Listing users
    - Getting user details
    - Updating user roles (admin/user)
    - Deleting users
    """

    def __init__(self, base_client: "BaseClient"):
        """
        Initialize the user manager.

        Args:
            base_client: The base client instance for making API requests
        """
        self.base_client = base_client

    def get_users(self, skip: int = 0, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        Get a list of all users.

        Args:
            skip: Number of users to skip (pagination)
            limit: Maximum number of users to return

        Returns:
            List of user objects or None if failed.
        """
        logger.info(f"Getting users list (skip={skip}, limit={limit})...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/users/",
                params={"skip": skip, "limit": limit},
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            users = response.json()
            logger.info(f"Successfully retrieved {len(users)} users.")
            return users
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get users: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting users: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific user by their ID.

        Args:
            user_id: The user's ID

        Returns:
            User object or None if not found/failed.
        """
        logger.info(f"Getting user details for ID: {user_id}...")
        try:
            response = self.base_client.session.get(
                f"{self.base_client.base_url}/api/v1/users/{user_id}",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            user = response.json()
            logger.info(f"Successfully retrieved user details for {user_id}.")
            return user
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None

    def update_user_role(self, user_id: str, role: str) -> bool:
        """
        Update a user's role.

        Args:
            user_id: The user's ID
            role: The new role ("admin" or "user")

        Returns:
            True if successful, False otherwise.
        """
        logger.info(f"Updating role for user {user_id} to '{role}'...")

        if role not in ["admin", "user"]:
            logger.error(f"Invalid role '{role}'. Must be 'admin' or 'user'.")
            return False

        try:
            payload = {"role": role}
            response = self.base_client.session.post(
                f"{self.base_client.base_url}/api/v1/users/{user_id}/update/role",
                json=payload,
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            logger.info(f"Successfully updated role for user {user_id}.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update user role: {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.

        Args:
            user_id: The user's ID

        Returns:
            True if successful, False otherwise.
        """
        logger.info(f"Deleting user {user_id}...")
        try:
            response = self.base_client.session.delete(
                f"{self.base_client.base_url}/api/v1/users/{user_id}",
                headers=self.base_client.json_headers
            )
            response.raise_for_status()
            logger.info(f"Successfully deleted user {user_id}.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete user: {e}")
            return False
