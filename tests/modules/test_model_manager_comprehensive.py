"""
Comprehensive tests for ModelManager - covering remaining untested methods.
"""

import json
import unittest
from unittest.mock import Mock, patch

import requests

from openwebui_chat_client.modules.model_manager import ModelManager


class TestModelManagerComprehensive(unittest.TestCase):
    """Comprehensive test cases for ModelManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.base_client = Mock()
        self.base_client.base_url = "http://test-server.com"
        self.base_client.session = Mock()
        self.base_client.json_headers = {"Content-Type": "application/json"}
        self.model_manager = ModelManager(self.base_client, skip_initial_refresh=True)

    # ========== list_base_models tests ==========

    def test_list_base_models_success(self):
        """Test list_base_models returns base models successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "base-model-1", "name": "Base Model 1"},
                {"id": "base-model-2", "name": "Base Model 2"},
            ]
        }
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_base_models()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "base-model-1")

    def test_list_base_models_no_data_key(self):
        """Test list_base_models handles response without 'data' key."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}  # Wrong key
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_base_models()

        self.assertIsNone(result)

    def test_list_base_models_data_not_list(self):
        """Test list_base_models handles 'data' that is not a list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "not a list"}
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_base_models()

        self.assertIsNone(result)

    def test_list_base_models_request_exception(self):
        """Test list_base_models handles request exceptions."""
        mock_response = Mock()
        mock_response.text = "Server error"
        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Connection error", response=mock_response
        )

        result = self.model_manager.list_base_models()

        self.assertIsNone(result)

    def test_list_base_models_json_decode_error(self):
        """Test list_base_models handles JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_base_models()

        self.assertIsNone(result)

    # ========== list_custom_models tests ==========

    def test_list_custom_models_success(self):
        """Test list_custom_models returns custom models successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "custom-1", "name": "Custom Model 1"},
            {"id": "custom-2", "name": "Custom Model 2"},
        ]
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_custom_models()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "custom-1")

    def test_list_custom_models_not_list(self):
        """Test list_custom_models handles response that is not a list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}  # Dict instead of list
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_custom_models()

        self.assertIsNone(result)

    def test_list_custom_models_request_exception(self):
        """Test list_custom_models handles request exceptions."""
        mock_response = Mock()
        mock_response.text = "Server error"
        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Connection error", response=mock_response
        )

        result = self.model_manager.list_custom_models()

        self.assertIsNone(result)

    def test_list_custom_models_json_decode_error(self):
        """Test list_custom_models handles JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_custom_models()

        self.assertIsNone(result)

    # ========== list_groups tests ==========

    def test_list_groups_success(self):
        """Test list_groups returns groups successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "group-1", "name": "Group 1"},
            {"id": "group-2", "name": "Group 2"},
        ]
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_groups()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "group-1")

    def test_list_groups_not_list(self):
        """Test list_groups handles response that is not a list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"groups": []}  # Dict instead of list
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_groups()

        self.assertIsNone(result)

    def test_list_groups_request_exception(self):
        """Test list_groups handles request exceptions."""
        mock_response = Mock()
        mock_response.text = "Server error"
        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Connection error", response=mock_response
        )

        result = self.model_manager.list_groups()

        self.assertIsNone(result)

    def test_list_groups_json_decode_error(self):
        """Test list_groups handles JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.list_groups()

        self.assertIsNone(result)

    # ========== get_model tests ==========

    def test_get_model_empty_id(self):
        """Test get_model with empty model ID."""
        result = self.model_manager.get_model("")

        self.assertIsNone(result)

    def test_get_model_not_in_available_models(self):
        """Test get_model when model is not in available models list."""
        self.model_manager.available_model_ids = ["model-1", "model-2"]

        with patch.object(
            self.model_manager, "_refresh_available_models"
        ) as mock_refresh:
            result = self.model_manager.get_model("nonexistent-model")

        mock_refresh.assert_called_once()
        self.assertIsNone(result)

    def test_get_model_401_auto_create_success(self):
        """Test get_model auto-creates model on 401 response."""
        self.model_manager.available_model_ids = ["test-model"]

        # First call returns 401, second call succeeds
        mock_response_401 = Mock()
        mock_response_401.status_code = 401

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "id": "test-model",
            "name": "Test Model",
        }

        self.base_client.session.get.side_effect = [
            mock_response_401,
            mock_response_success,
        ]

        with patch.object(
            self.model_manager, "create_model"
        ) as mock_create:
            mock_create.return_value = {"id": "test-model"}
            result = self.model_manager.get_model("test-model")

        mock_create.assert_called_once()
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "test-model")

    def test_get_model_401_auto_create_fails(self):
        """Test get_model when auto-create fails on 401."""
        self.model_manager.available_model_ids = ["test-model"]

        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        self.base_client.session.get.return_value = mock_response_401

        with patch.object(self.model_manager, "create_model") as mock_create:
            mock_create.return_value = None  # Creation fails
            result = self.model_manager.get_model("test-model")

        self.assertIsNone(result)

    def test_get_model_request_exception(self):
        """Test get_model handles request exceptions."""
        self.model_manager.available_model_ids = ["test-model"]

        mock_response = Mock()
        mock_response.text = "Server error"
        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Connection error", response=mock_response
        )

        result = self.model_manager.get_model("test-model")

        self.assertIsNone(result)

    def test_get_model_json_decode_error(self):
        """Test get_model handles JSON decode errors."""
        self.model_manager.available_model_ids = ["test-model"]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        self.base_client.session.get.return_value = mock_response

        result = self.model_manager.get_model("test-model")

        self.assertIsNone(result)

    # ========== delete_model tests ==========

    def test_delete_model_empty_id(self):
        """Test delete_model with empty model ID."""
        result = self.model_manager.delete_model("")

        self.assertFalse(result)

    def test_delete_model_success(self):
        """Test delete_model successfully deletes a model."""
        mock_response = Mock()
        mock_response.status_code = 200
        self.base_client.session.delete.return_value = mock_response

        with patch.object(
            self.model_manager, "_refresh_available_models"
        ) as mock_refresh:
            result = self.model_manager.delete_model("test-model")

        self.assertTrue(result)
        mock_refresh.assert_called_once()

    def test_delete_model_405_fallback_to_post(self):
        """Test delete_model falls back to POST on 405 error."""
        mock_response_405 = Mock()
        mock_response_405.status_code = 405

        mock_response_success = Mock()
        mock_response_success.status_code = 200

        self.base_client.session.delete.return_value = mock_response_405
        self.base_client.session.post.return_value = mock_response_success

        with patch.object(
            self.model_manager, "_refresh_available_models"
        ) as mock_refresh:
            result = self.model_manager.delete_model("test-model")

        self.assertTrue(result)
        self.base_client.session.post.assert_called_once()
        mock_refresh.assert_called_once()

    def test_delete_model_405_post_fallback_fails(self):
        """Test delete_model when POST fallback also fails."""
        mock_response_405 = Mock()
        mock_response_405.status_code = 405

        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("500 Server Error")
        )

        self.base_client.session.delete.return_value = mock_response_405
        self.base_client.session.post.return_value = mock_response_fail

        result = self.model_manager.delete_model("test-model")

        self.assertFalse(result)

    def test_delete_model_request_exception(self):
        """Test delete_model handles request exceptions."""
        mock_response = Mock()
        mock_response.text = "Server error"
        self.base_client.session.delete.side_effect = (
            requests.exceptions.RequestException(
                "Connection error", response=mock_response
            )
        )

        result = self.model_manager.delete_model("test-model")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
