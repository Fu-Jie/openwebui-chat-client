import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient


class TestModelPermissions(unittest.TestCase):
    """Unit tests for model permissions functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "http://localhost:3000"
        self.token = "test-token"
        self.default_model = "test-model:latest"
        
        # Create client with skip_model_refresh to prevent HTTP requests during initialization
        self.client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            skip_model_refresh=True,
        )
        self.client._auto_cleanup_enabled = False

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_list_groups_success(self, mock_get):
        """Test successful groups listing."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "000a5d15-dcf1-4197-9462-021b835c03f0",
                "user_id": "105ba5cd-c9a9-4bde-8de4-64462f021204",
                "name": "normal",
                "description": "",
                "permissions": {"workspace": {"models": True}},
                "user_ids": ["user1", "user2"]
            },
            {
                "id": "111b6e26-edf2-5208-a573-132c73f0f1f1",
                "user_id": "105ba5cd-c9a9-4bde-8de4-64462f021204",
                "name": "admin",
                "description": "Admin group",
                "permissions": {"workspace": {"models": True}},
                "user_ids": ["admin1"]
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.list_groups()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "normal")
        self.assertEqual(result[1]["name"], "admin")
        mock_get.assert_called_once_with(
            f"{self.base_url}/api/v1/groups/",
            headers=self.client.json_headers
        )

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.get")
    def test_list_groups_failure(self, mock_get):
        """Test groups listing failure."""
        from requests.exceptions import RequestException
        
        mock_get.side_effect = RequestException("Network error")

        result = self.client.list_groups()

        self.assertIsNone(result)

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_update_model_with_access_control_none_for_public(self, mock_post):
        """Test updating model with access_control=None for public permissions."""
        # Mock get_model to return existing model
        existing_model = {
            "id": "test-model",
            "name": "Test Model",
            "base_model_id": "base-model",
            "params": {},
            "meta": {"capabilities": {}}
        }
        
        with patch.object(self.client, 'get_model', return_value=existing_model):
            mock_response = Mock()
            mock_response.json.return_value = {"id": "test-model", "updated": True}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # Test with access_control=None for public permissions
            result = self.client.update_model("test-model", access_control=None)

            self.assertIsNotNone(result)
            self.assertEqual(result["id"], "test-model")
            
            # Verify the payload included access_control set to None
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            self.assertIn("access_control", payload)
            self.assertIsNone(payload["access_control"])

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_update_model_without_access_control_parameter(self, mock_post):
        """Test updating model without providing access_control parameter."""
        # Mock get_model to return existing model
        existing_model = {
            "id": "test-model",
            "name": "Test Model",
            "base_model_id": "base-model",
            "params": {},
            "meta": {"capabilities": {}},
            "access_control": {"read": {"group_ids": ["existing"], "user_ids": []}}
        }
        
        with patch.object(self.client, 'get_model', return_value=existing_model):
            mock_response = Mock()
            mock_response.json.return_value = {"id": "test-model", "updated": True}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # Test without access_control parameter - should preserve existing
            result = self.client.update_model("test-model", name="New Name")

            self.assertIsNotNone(result)
            self.assertEqual(result["id"], "test-model")
            
            # Verify the payload preserved existing access_control
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            self.assertEqual(payload["access_control"], {"read": {"group_ids": ["existing"], "user_ids": []}})

    @patch("openwebui_chat_client.openwebui_chat_client.requests.Session.post")
    def test_update_model_with_access_control(self, mock_post):
        """Test updating model with access control."""
        # Mock get_model to return existing model
        existing_model = {
            "id": "test-model",
            "name": "Test Model",
            "base_model_id": "base-model",
            "params": {},
            "meta": {"capabilities": {}}
        }
        
        with patch.object(self.client, 'get_model', return_value=existing_model):
            mock_response = Mock()
            mock_response.json.return_value = {"id": "test-model", "updated": True}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            access_control = {
                "read": {"group_ids": ["group1"], "user_ids": []},
                "write": {"group_ids": ["group1"], "user_ids": []}
            }

            result = self.client.update_model("test-model", access_control=access_control)

            self.assertIsNotNone(result)
            self.assertEqual(result["id"], "test-model")
            
            # Verify the payload included access_control
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            self.assertEqual(payload["access_control"], access_control)

    def test_build_access_control_public(self):
        """Test building public access control."""
        result = self.client._build_access_control("public")
        self.assertIsNone(result)

    def test_build_access_control_private(self):
        """Test building private access control."""
        result = self.client._build_access_control("private", user_ids=["user1", "user2"])
        expected = {
            "read": {"group_ids": [], "user_ids": ["user1", "user2"]},
            "write": {"group_ids": [], "user_ids": ["user1", "user2"]}
        }
        self.assertEqual(result, expected)

    def test_build_access_control_group_with_ids(self):
        """Test building group access control with group IDs."""
        with patch.object(self.client, '_resolve_group_ids', return_value=["group1", "group2"]):
            result = self.client._build_access_control("group", group_identifiers=["group1", "group2"])
            expected = {
                "read": {"group_ids": ["group1", "group2"], "user_ids": []},
                "write": {"group_ids": ["group1", "group2"], "user_ids": []}
            }
            self.assertEqual(result, expected)

    def test_build_access_control_invalid_type(self):
        """Test building access control with invalid type."""
        result = self.client._build_access_control("invalid")
        self.assertFalse(result)

    def test_resolve_group_ids_with_names_and_ids(self):
        """Test resolving group names to IDs."""
        mock_groups = [
            {"id": "id1", "name": "normal"},
            {"id": "id2", "name": "admin"}
        ]
        
        with patch.object(self.client, 'list_groups', return_value=mock_groups):
            result = self.client._resolve_group_ids(["normal", "id2", "admin"])
            self.assertEqual(result, ["id1", "id2", "id2"])

    def test_resolve_group_ids_invalid_identifier(self):
        """Test resolving group IDs with invalid identifier."""
        mock_groups = [
            {"id": "id1", "name": "normal"},
            {"id": "id2", "name": "admin"}
        ]
        
        with patch.object(self.client, 'list_groups', return_value=mock_groups):
            result = self.client._resolve_group_ids(["nonexistent"])
            self.assertFalse(result)

    def test_resolve_group_ids_no_groups(self):
        """Test resolving group IDs when group listing fails."""
        with patch.object(self.client, 'list_groups', return_value=None):
            result = self.client._resolve_group_ids(["normal"])
            self.assertFalse(result)

    @patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor")
    def test_batch_update_model_permissions_with_model_ids(self, mock_executor):
        """Test batch update with specific model IDs."""
        mock_model = {"id": "test-model", "name": "Test Model"}
        
        # Mock the ThreadPoolExecutor context manager
        mock_context = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_context
        mock_executor.return_value.__exit__.return_value = None
        
        # Mock concurrent.futures.as_completed
        with patch("openwebui_chat_client.openwebui_chat_client.as_completed") as mock_as_completed:
            mock_future = MagicMock()
            mock_future.result.return_value = ("test-model", True, "success")
            mock_as_completed.return_value = [mock_future]
            mock_context.submit.return_value = mock_future
            
            with patch.object(self.client, 'get_model', return_value=mock_model):
                with patch.object(self.client, '_build_access_control', return_value=None):
                    result = self.client.batch_update_model_permissions(
                        model_identifiers=["test-model"],
                        permission_type="public"
                    )

            self.assertEqual(len(result["success"]), 1)
            self.assertEqual(result["success"][0], "test-model")
            self.assertEqual(len(result["failed"]), 0)

    def test_batch_update_model_permissions_with_keyword(self):
        """Test batch update with keyword filtering."""
        mock_models = [
            {"id": "gpt-4", "name": "GPT-4"},
            {"id": "gpt-3.5", "name": "GPT-3.5"},
            {"id": "claude", "name": "Claude"}
        ]
        
        with patch.object(self.client, 'list_models', return_value=mock_models):
            with patch.object(self.client, '_build_access_control', return_value=None):
                with patch("openwebui_chat_client.openwebui_chat_client.ThreadPoolExecutor") as mock_executor:
                    mock_context = MagicMock()
                    mock_executor.return_value.__enter__.return_value = mock_context
                    mock_executor.return_value.__exit__.return_value = None
                    
                    with patch("openwebui_chat_client.openwebui_chat_client.as_completed") as mock_as_completed:
                        mock_future = MagicMock()
                        mock_future.result.return_value = ("gpt-4", True, "success")
                        mock_as_completed.return_value = [mock_future]
                        mock_context.submit.return_value = mock_future
                        
                        result = self.client.batch_update_model_permissions(
                            model_keyword="gpt",
                            permission_type="public"
                        )
                
                # Should find 2 models with "gpt" in the name/id
                self.assertEqual(len(result["success"]), 1)  # Only one mock future returned

    def test_batch_update_model_permissions_invalid_permission_type(self):
        """Test batch update with invalid permission type."""
        result = self.client.batch_update_model_permissions(
            model_identifiers=["test-model"],
            permission_type="invalid"
        )
        
        self.assertEqual(len(result["success"]), 0)
        self.assertEqual(len(result["failed"]), 0)
        self.assertEqual(len(result["skipped"]), 0)

    def test_batch_update_model_permissions_no_models_found(self):
        """Test batch update when no models are found."""
        with patch.object(self.client, 'get_model', return_value=None):
            result = self.client.batch_update_model_permissions(
                model_identifiers=["nonexistent-model"],
                permission_type="public"
            )
            
            self.assertEqual(len(result["success"]), 0)
            self.assertEqual(len(result["failed"]), 0)

    def test_batch_update_model_permissions_failed_models_list(self):
        """Test batch update when models list fails."""
        with patch.object(self.client, 'list_models', return_value=None):
            result = self.client.batch_update_model_permissions(
                model_keyword="test",
                permission_type="public"
            )
            
            self.assertEqual(len(result["success"]), 0)
            self.assertEqual(len(result["failed"]), 0)


if __name__ == "__main__":
    unittest.main()