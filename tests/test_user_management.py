"""
Unit tests for user management functionality in OpenWebUI Chat Client.
Tests the UserManager class and related functionality.
"""

import unittest
from unittest.mock import Mock, patch
import requests

# Import the classes to test
from openwebui_chat_client import OpenWebUIClient
from openwebui_chat_client.modules.user_manager import UserManager


class TestUserManager(unittest.TestCase):
    """Test cases for UserManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = Mock()
        self.base_client.base_url = "http://localhost:3000"
        self.base_client.session = Mock()
        self.base_client.json_headers = {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }
        self.user_manager = UserManager(self.base_client)

    def test_initialization(self):
        """Test user manager initialization."""
        self.assertEqual(self.user_manager.base_client, self.base_client)

    def test_get_users_success(self):
        """Test successful retrieval of users."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "user123",
                "name": "User One",
                "email": "user1@example.com",
                "role": "user"
            }
        ]
        mock_response.raise_for_status.return_value = None
        self.base_client.session.get.return_value = mock_response

        result = self.user_manager.get_users(skip=0, limit=10)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "user123")
        self.base_client.session.get.assert_called_once_with(
            "http://localhost:3000/api/v1/users/",
            params={"skip": 0, "limit": 10},
            headers=self.base_client.json_headers
        )

    def test_get_users_failure(self):
        """Test users retrieval failure."""
        self.base_client.session.get.side_effect = requests.exceptions.RequestException("Network error")

        result = self.user_manager.get_users()

        self.assertIsNone(result)

    def test_get_user_by_id_success(self):
        """Test successful retrieval of user by ID."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "user123",
            "name": "User One",
            "role": "user"
        }
        mock_response.raise_for_status.return_value = None
        self.base_client.session.get.return_value = mock_response

        result = self.user_manager.get_user_by_id("user123")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "user123")
        self.base_client.session.get.assert_called_once_with(
            "http://localhost:3000/api/v1/users/user123",
            headers=self.base_client.json_headers
        )

    def test_get_user_by_id_failure(self):
        """Test user retrieval failure."""
        self.base_client.session.get.side_effect = requests.exceptions.RequestException("Network error")

        result = self.user_manager.get_user_by_id("user123")

        self.assertIsNone(result)

    def test_update_user_role_success(self):
        """Test successful user role update."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        self.base_client.session.post.return_value = mock_response

        result = self.user_manager.update_user_role("user123", "admin")

        self.assertTrue(result)
        self.base_client.session.post.assert_called_once_with(
            "http://localhost:3000/api/v1/users/user123/update/role",
            json={"role": "admin"},
            headers=self.base_client.json_headers
        )

    def test_update_user_role_invalid_role(self):
        """Test user role update with invalid role."""
        result = self.user_manager.update_user_role("user123", "superadmin")

        self.assertFalse(result)
        self.base_client.session.post.assert_not_called()

    def test_update_user_role_failure(self):
        """Test user role update failure."""
        self.base_client.session.post.side_effect = requests.exceptions.RequestException("Network error")

        result = self.user_manager.update_user_role("user123", "admin")

        self.assertFalse(result)

    def test_delete_user_success(self):
        """Test successful user deletion."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        self.base_client.session.delete.return_value = mock_response

        result = self.user_manager.delete_user("user123")

        self.assertTrue(result)
        self.base_client.session.delete.assert_called_once_with(
            "http://localhost:3000/api/v1/users/user123",
            headers=self.base_client.json_headers
        )

    def test_delete_user_failure(self):
        """Test user deletion failure."""
        self.base_client.session.delete.side_effect = requests.exceptions.RequestException("Network error")

        result = self.user_manager.delete_user("user123")

        self.assertFalse(result)


class TestOpenWebUIClientUserIntegration(unittest.TestCase):
    """Test user management integration with OpenWebUIClient."""

    def setUp(self):
        """Set up test client."""
        with patch('openwebui_chat_client.openwebui_chat_client.ModelManager'):
            self.client = OpenWebUIClient(
                base_url="http://localhost:3000",
                token="test_token",
                default_model_id="test-model",
                skip_model_refresh=True
            )

    def test_user_manager_initialized(self):
        """Test that user manager is properly initialized."""
        self.assertIsNotNone(self.client._user_manager)
        self.assertEqual(
            self.client._user_manager.base_client,
            self.client._base_client
        )

    def test_user_methods_delegated(self):
        """Test that user methods are properly delegated."""
        self.assertTrue(hasattr(self.client, 'get_users'))
        self.assertTrue(hasattr(self.client, 'get_user_by_id'))
        self.assertTrue(hasattr(self.client, 'update_user_role'))
        self.assertTrue(hasattr(self.client, 'delete_user'))

    def test_get_users_delegation(self):
        """Test get_users method delegation."""
        with patch.object(self.client._user_manager, 'get_users', return_value=[]) as mock_method:
            self.client.get_users(skip=10, limit=20)
            mock_method.assert_called_once_with(10, 20)

    def test_update_user_role_delegation(self):
        """Test update_user_role method delegation."""
        with patch.object(self.client._user_manager, 'update_user_role', return_value=True) as mock_method:
            self.client.update_user_role("user1", "admin")
            mock_method.assert_called_once_with("user1", "admin")


if __name__ == '__main__':
    unittest.main()
