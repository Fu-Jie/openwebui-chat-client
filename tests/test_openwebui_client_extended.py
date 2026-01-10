"""
Extended tests for OpenWebUIClient to improve coverage.

This test file focuses on testing methods in the main OpenWebUIClient class
that delegate to managers and handle complex operations.
"""

import json
import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

from openwebui_chat_client import OpenWebUIClient


class TestOpenWebUIClientExtended(unittest.TestCase):
    """Extended tests for OpenWebUIClient main class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "http://localhost:3000"
        self.token = "test_token"
        self.default_model = "test-model"

        # Create client with mocked managers
        with patch("openwebui_chat_client.openwebui_chat_client.ModelManager"):
            with patch("openwebui_chat_client.openwebui_chat_client.ChatManager"):
                with patch(
                    "openwebui_chat_client.openwebui_chat_client.KnowledgeBaseManager"
                ):
                    with patch(
                        "openwebui_chat_client.openwebui_chat_client.NotesManager"
                    ):
                        with patch(
                            "openwebui_chat_client.openwebui_chat_client.PromptsManager"
                        ):
                            with patch(
                                "openwebui_chat_client.openwebui_chat_client.UserManager"
                            ):
                                with patch(
                                    "openwebui_chat_client.openwebui_chat_client.FileManager"
                                ):
                                    self.client = OpenWebUIClient(
                                        self.base_url,
                                        self.token,
                                        self.default_model,
                                        skip_model_refresh=True,
                                    )

    def test_initialization_properties(self):
        """Test that client properties are correctly initialized."""
        self.assertEqual(self.client.base_url, self.base_url)
        self.assertEqual(self.client.default_model_id, self.default_model)
        self.assertIsNotNone(self.client.session)
        self.assertIsNotNone(self.client.json_headers)

    def test_property_setters(self):
        """Test property setters work correctly."""
        # Test chat_id setter
        test_chat_id = "test_chat_123"
        self.client.chat_id = test_chat_id
        self.assertEqual(self.client._base_client.chat_id, test_chat_id)

        # Test model_id setter
        test_model_id = "new-model"
        self.client.model_id = test_model_id
        self.assertEqual(self.client._base_client.model_id, test_model_id)

        # Test chat_object_from_server setter
        test_chat_obj = {"id": "123", "title": "Test"}
        self.client.chat_object_from_server = test_chat_obj
        self.assertEqual(
            self.client._base_client.chat_object_from_server, test_chat_obj
        )

    def test_available_model_ids_property(self):
        """Test available_model_ids property getter and setter."""
        test_models = ["model1", "model2", "model3"]
        self.client._model_manager.available_model_ids = test_models

        # Test getter
        self.assertEqual(self.client.available_model_ids, test_models)

        # Test setter
        new_models = ["model4", "model5"]
        self.client.available_model_ids = new_models
        self.assertEqual(self.client._model_manager.available_model_ids, new_models)
        self.assertEqual(self.client._base_client.available_model_ids, new_models)

    def test_build_access_control_public(self):
        """Test _build_access_control with public permission."""
        result = self.client._build_access_control("public")
        self.assertIsNone(result)

    def test_build_access_control_private(self):
        """Test _build_access_control with private permission."""
        user_ids = ["user1", "user2"]
        result = self.client._build_access_control("private", user_ids=user_ids)

        self.assertIsInstance(result, dict)
        self.assertIn("read", result)
        self.assertIn("write", result)
        self.assertEqual(result["read"]["user_ids"], user_ids)
        self.assertEqual(result["write"]["user_ids"], user_ids)
        self.assertEqual(result["read"]["group_ids"], [])

    def test_build_access_control_group_no_identifiers(self):
        """Test _build_access_control with group permission but no identifiers."""
        result = self.client._build_access_control("group")
        self.assertFalse(result)

    @patch.object(OpenWebUIClient, "list_groups")
    def test_resolve_group_ids_success(self, mock_list_groups):
        """Test _resolve_group_ids successfully resolves group names to IDs."""
        mock_list_groups.return_value = [
            {"id": "group1_id", "name": "Group 1"},
            {"id": "group2_id", "name": "Group 2"},
        ]

        result = self.client._resolve_group_ids(["Group 1", "group2_id"])
        self.assertEqual(result, ["group1_id", "group2_id"])

    @patch.object(OpenWebUIClient, "list_groups")
    def test_resolve_group_ids_not_found(self, mock_list_groups):
        """Test _resolve_group_ids returns False when group not found."""
        mock_list_groups.return_value = [
            {"id": "group1_id", "name": "Group 1"},
        ]

        result = self.client._resolve_group_ids(["NonExistent"])
        self.assertFalse(result)

    @patch.object(OpenWebUIClient, "list_groups")
    def test_resolve_group_ids_list_failure(self, mock_list_groups):
        """Test _resolve_group_ids returns False when list_groups fails."""
        mock_list_groups.return_value = None

        result = self.client._resolve_group_ids(["Group 1"])
        self.assertFalse(result)

    def test_build_access_control_invalid_type(self):
        """Test _build_access_control with invalid permission type."""
        result = self.client._build_access_control("invalid_type")
        self.assertFalse(result)

    @patch.object(OpenWebUIClient, "_resolve_group_ids")
    def test_build_access_control_group_success(self, mock_resolve):
        """Test _build_access_control with group permission."""
        mock_resolve.return_value = ["group1_id", "group2_id"]

        result = self.client._build_access_control(
            "group", group_identifiers=["Group 1", "Group 2"], user_ids=["user1"]
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["read"]["group_ids"], ["group1_id", "group2_id"])
        self.assertEqual(result["read"]["user_ids"], ["user1"])

    @patch.object(OpenWebUIClient, "_resolve_group_ids")
    def test_build_access_control_group_resolve_failure(self, mock_resolve):
        """Test _build_access_control when group resolution fails."""
        mock_resolve.return_value = False

        result = self.client._build_access_control(
            "group", group_identifiers=["Group 1"]
        )

        self.assertFalse(result)


class TestOpenWebUIClientBatchOperations(unittest.TestCase):
    """Test batch operations in OpenWebUIClient."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("openwebui_chat_client.openwebui_chat_client.ModelManager"):
            with patch("openwebui_chat_client.openwebui_chat_client.ChatManager"):
                with patch(
                    "openwebui_chat_client.openwebui_chat_client.KnowledgeBaseManager"
                ):
                    with patch(
                        "openwebui_chat_client.openwebui_chat_client.NotesManager"
                    ):
                        with patch(
                            "openwebui_chat_client.openwebui_chat_client.PromptsManager"
                        ):
                            with patch(
                                "openwebui_chat_client.openwebui_chat_client.UserManager"
                            ):
                                with patch(
                                    "openwebui_chat_client.openwebui_chat_client.FileManager"
                                ):
                                    self.client = OpenWebUIClient(
                                        "http://localhost:3000",
                                        "test_token",
                                        "test-model",
                                        skip_model_refresh=True,
                                    )

    @patch.object(OpenWebUIClient, "update_model")
    @patch.object(OpenWebUIClient, "_build_access_control")
    def test_batch_update_model_permissions_with_models(
        self, mock_build_access, mock_update
    ):
        """Test batch_update_model_permissions with models list."""
        mock_build_access.return_value = {"read": {"group_ids": [], "user_ids": []}}
        mock_update.return_value = {"id": "model1"}

        models = [{"id": "model1"}, {"id": "model2"}]
        result = self.client.batch_update_model_permissions(
            models=models, permission_type="public"
        )

        self.assertEqual(len(result["success"]), 2)
        self.assertEqual(len(result["failed"]), 0)

    @patch.object(OpenWebUIClient, "get_model")
    @patch.object(OpenWebUIClient, "update_model")
    @patch.object(OpenWebUIClient, "_build_access_control")
    def test_batch_update_model_permissions_with_identifiers(
        self, mock_build_access, mock_update, mock_get
    ):
        """Test batch_update_model_permissions with model_identifiers."""
        mock_build_access.return_value = {"read": {"group_ids": [], "user_ids": []}}
        mock_get.return_value = {"id": "model1", "name": "Model 1"}
        mock_update.return_value = {"id": "model1"}

        result = self.client.batch_update_model_permissions(
            model_identifiers=["model1"], permission_type="public"
        )

        self.assertEqual(len(result["success"]), 1)

    @patch.object(OpenWebUIClient, "list_models")
    @patch.object(OpenWebUIClient, "update_model")
    @patch.object(OpenWebUIClient, "_build_access_control")
    def test_batch_update_model_permissions_with_keyword(
        self, mock_build_access, mock_update, mock_list
    ):
        """Test batch_update_model_permissions with model_keyword."""
        mock_build_access.return_value = {"read": {"group_ids": [], "user_ids": []}}
        mock_list.return_value = [
            {"id": "test-model-1", "name": "Test Model 1"},
            {"id": "test-model-2", "name": "Test Model 2"},
            {"id": "other-model", "name": "Other Model"},
        ]
        mock_update.return_value = {"id": "test-model-1"}

        result = self.client.batch_update_model_permissions(
            model_keyword="test", permission_type="public"
        )

        self.assertEqual(len(result["success"]), 2)

    @patch.object(OpenWebUIClient, "_build_access_control")
    def test_batch_update_model_permissions_invalid_permission_type(
        self, mock_build_access
    ):
        """Test batch_update_model_permissions with invalid permission type."""
        result = self.client.batch_update_model_permissions(
            models=[{"id": "model1"}], permission_type="invalid"
        )

        self.assertEqual(len(result["success"]), 0)
        self.assertEqual(len(result["failed"]), 0)
        self.assertEqual(len(result["skipped"]), 0)

    def test_batch_update_model_permissions_no_parameters(self):
        """Test batch_update_model_permissions with no models specified."""
        result = self.client.batch_update_model_permissions(permission_type="public")

        self.assertEqual(len(result["success"]), 0)
        self.assertEqual(len(result["failed"]), 0)

    @patch.object(OpenWebUIClient, "list_models")
    @patch.object(OpenWebUIClient, "_build_access_control")
    def test_batch_update_model_permissions_keyword_no_matches(
        self, mock_build_access, mock_list
    ):
        """Test batch_update_model_permissions with keyword that matches nothing."""
        mock_build_access.return_value = {"read": {"group_ids": [], "user_ids": []}}
        mock_list.return_value = [
            {"id": "model1", "name": "Model 1"},
        ]

        result = self.client.batch_update_model_permissions(
            model_keyword="nonexistent", permission_type="public"
        )

        self.assertEqual(len(result["success"]), 0)

    @patch.object(OpenWebUIClient, "update_model")
    @patch.object(OpenWebUIClient, "_build_access_control")
    def test_batch_update_model_permissions_update_failure(
        self, mock_build_access, mock_update
    ):
        """Test batch_update_model_permissions when update fails."""
        mock_build_access.return_value = {"read": {"group_ids": [], "user_ids": []}}
        mock_update.return_value = None  # Simulate failure

        models = [{"id": "model1"}]
        result = self.client.batch_update_model_permissions(
            models=models, permission_type="public"
        )

        self.assertEqual(len(result["success"]), 0)
        self.assertEqual(len(result["failed"]), 1)

    @patch.object(OpenWebUIClient, "update_model")
    @patch.object(OpenWebUIClient, "_build_access_control")
    def test_batch_update_model_permissions_exception(
        self, mock_build_access, mock_update
    ):
        """Test batch_update_model_permissions when exception occurs."""
        mock_build_access.return_value = {"read": {"group_ids": [], "user_ids": []}}
        mock_update.side_effect = Exception("Update failed")

        models = [{"id": "model1"}]
        result = self.client.batch_update_model_permissions(
            models=models, permission_type="public"
        )

        self.assertEqual(len(result["success"]), 0)
        self.assertEqual(len(result["failed"]), 1)


if __name__ == "__main__":
    unittest.main()
