"""
Tests for AsyncUserManager module.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from openwebui_chat_client.modules.async_user_manager import AsyncUserManager

pytestmark = pytest.mark.asyncio


class TestAsyncUserManager:
    """Test cases for AsyncUserManager class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.base_client = Mock()
        self.base_client._make_request = AsyncMock()
        self.base_client._get_json_response = AsyncMock()
        self.manager = AsyncUserManager(self.base_client)

    def test_initialization(self):
        """Test AsyncUserManager initialization"""
        assert self.manager.base_client == self.base_client

    async def test_get_users_default_params(self):
        """Test getting users with default parameters"""
        expected_users = [
            {"id": "user1", "name": "User 1", "role": "user"},
            {"id": "user2", "name": "User 2", "role": "admin"},
        ]
        self.base_client._get_json_response.return_value = expected_users

        result = await self.manager.get_users()

        assert result == expected_users
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/users/", params={"skip": 0, "limit": 50}
        )

    async def test_get_users_custom_params(self):
        """Test getting users with custom skip and limit"""
        expected_users = [{"id": "user3", "name": "User 3"}]
        self.base_client._get_json_response.return_value = expected_users

        result = await self.manager.get_users(skip=10, limit=20)

        assert result == expected_users
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/users/", params={"skip": 10, "limit": 20}
        )

    async def test_get_users_empty_list(self):
        """Test getting users returns empty list"""
        self.base_client._get_json_response.return_value = []

        result = await self.manager.get_users()

        assert result == []

    async def test_get_users_none_response(self):
        """Test getting users when request fails"""
        self.base_client._get_json_response.return_value = None

        result = await self.manager.get_users()

        assert result is None

    async def test_get_user_by_id_success(self):
        """Test getting user by ID successfully"""
        expected_user = {
            "id": "user123",
            "name": "Test User",
            "email": "test@example.com",
            "role": "user",
        }
        self.base_client._get_json_response.return_value = expected_user

        result = await self.manager.get_user_by_id("user123")

        assert result == expected_user
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/users/user123"
        )

    async def test_get_user_by_id_not_found(self):
        """Test getting user by ID when not found"""
        self.base_client._get_json_response.return_value = None

        result = await self.manager.get_user_by_id("nonexistent")

        assert result is None

    async def test_get_user_by_id_empty_id(self):
        """Test getting user with empty ID"""
        expected_user = {"error": "Invalid ID"}
        self.base_client._get_json_response.return_value = expected_user

        result = await self.manager.get_user_by_id("")

        assert result == expected_user
        self.base_client._get_json_response.assert_called_once_with(
            "GET", "/api/v1/users/"
        )

    async def test_update_user_role_to_admin(self):
        """Test updating user role to admin"""
        mock_response = Mock()
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.update_user_role("user123", "admin")

        assert result is True
        self.base_client._make_request.assert_called_once_with(
            "POST", "/api/v1/users/user123/update/role", json_data={"role": "admin"}
        )

    async def test_update_user_role_to_user(self):
        """Test updating user role to user"""
        mock_response = Mock()
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.update_user_role("user123", "user")

        assert result is True
        self.base_client._make_request.assert_called_once_with(
            "POST", "/api/v1/users/user123/update/role", json_data={"role": "user"}
        )

    async def test_update_user_role_invalid_role(self):
        """Test updating user role with invalid role"""
        result = await self.manager.update_user_role("user123", "superadmin")

        assert result is False
        self.base_client._make_request.assert_not_called()

    async def test_update_user_role_empty_role(self):
        """Test updating user role with empty role"""
        result = await self.manager.update_user_role("user123", "")

        assert result is False
        self.base_client._make_request.assert_not_called()

    async def test_update_user_role_request_fails(self):
        """Test updating user role when request fails"""
        self.base_client._make_request.return_value = None

        result = await self.manager.update_user_role("user123", "admin")

        assert result is False

    async def test_delete_user_success(self):
        """Test deleting user successfully"""
        mock_response = Mock()
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.delete_user("user123")

        assert result is True
        self.base_client._make_request.assert_called_once_with(
            "DELETE", "/api/v1/users/user123"
        )

    async def test_delete_user_not_found(self):
        """Test deleting user when not found"""
        self.base_client._make_request.return_value = None

        result = await self.manager.delete_user("nonexistent")

        assert result is False

    async def test_delete_user_empty_id(self):
        """Test deleting user with empty ID"""
        mock_response = Mock()
        self.base_client._make_request.return_value = mock_response

        result = await self.manager.delete_user("")

        assert result is True
        self.base_client._make_request.assert_called_once_with(
            "DELETE", "/api/v1/users/"
        )

    async def test_update_user_role_case_sensitive(self):
        """Test that role validation is case sensitive"""
        # Should fail with uppercase
        result = await self.manager.update_user_role("user123", "Admin")
        assert result is False

        result = await self.manager.update_user_role("user123", "USER")
        assert result is False

        result = await self.manager.update_user_role("user123", "ADMIN")
        assert result is False
