"""
Extended tests for ModelManager to improve coverage.

This test file focuses on testing ModelManager methods including
CRUD operations, error handling, and edge cases.
"""

import json
import unittest
from unittest.mock import Mock, patch

import requests

from openwebui_chat_client.core.base_client import BaseClient
from openwebui_chat_client.modules.model_manager import ModelManager


class TestModelManagerExtended(unittest.TestCase):
    """Extended tests for ModelManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = Mock(spec=BaseClient)
        self.base_client.base_url = "http://localhost:3000"
        self.base_client.session = Mock()
        self.base_client.json_headers = {"Authorization": "Bearer test_token"}

        # Create manager with skip_initial_refresh=True to avoid API calls
        self.manager = ModelManager(self.base_client, skip_initial_refresh=True)

    def test_initialization_with_refresh(self):
        """Test ModelManager initialization with model refresh."""
        with patch.object(ModelManager, "_refresh_available_models") as mock_refresh:
            ModelManager(self.base_client, skip_initial_refresh=False)
            mock_refresh.assert_called_once()

    def test_refresh_available_models_success(self):
        """Test _refresh_available_models successfully updates model list."""
        mock_models = [
            {"id": "model1", "name": "Model 1"},
            {"id": "model2", "name": "Model 2"},
        ]

        with patch.object(self.manager, "list_models", return_value=mock_models):
            self.manager._refresh_available_models()

            self.assertEqual(self.manager.available_model_ids, ["model1", "model2"])

    def test_refresh_available_models_no_models(self):
        """Test _refresh_available_models when no models returned."""
        with patch.object(self.manager, "list_models", return_value=None):
            self.manager._refresh_available_models()

            self.assertEqual(self.manager.available_model_ids, [])

    def test_refresh_available_models_empty_list(self):
        """Test _refresh_available_models with empty model list."""
        with patch.object(self.manager, "list_models", return_value=[]):
            self.manager._refresh_available_models()

            self.assertEqual(self.manager.available_model_ids, [])

    def test_list_models_invalid_response_format(self):
        """Test list_models with invalid response format."""
        mock_response = Mock()
        mock_response.json.return_value = {"invalid": "format"}
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.list_models()

        self.assertIsNone(result)

    def test_list_models_data_not_list(self):
        """Test list_models when data is not a list."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "not a list"}
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.list_models()

        self.assertIsNone(result)

    def test_list_models_json_decode_error(self):
        """Test list_models handles JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.list_models()

        self.assertIsNone(result)

    def test_list_models_request_exception_with_response(self):
        """Test list_models handles request exception with response."""
        mock_response = Mock()
        mock_response.text = "Error message"
        error = requests.exceptions.RequestException("API Error")
        error.response = mock_response
        self.base_client.session.get.side_effect = error

        result = self.manager.list_models()

        self.assertIsNone(result)

    def test_list_base_models_invalid_format(self):
        """Test list_base_models with invalid response format."""
        mock_response = Mock()
        mock_response.json.return_value = {"invalid": "format"}
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.list_base_models()

        self.assertIsNone(result)

    def test_list_base_models_json_decode_error(self):
        """Test list_base_models handles JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.list_base_models()

        self.assertIsNone(result)

    def test_list_custom_models_success(self):
        """Test list_custom_models successfully filters custom models."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "custom1", "name": "Custom 1", "base_model_id": "base1"},
            {"id": "custom2", "name": "Custom 2", "base_model_id": "base2"},
        ]
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.list_custom_models()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

    def test_list_custom_models_invalid_format(self):
        """Test list_custom_models with invalid response format."""
        mock_response = Mock()
        mock_response.json.return_value = {"invalid": "format"}
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.list_custom_models()

        self.assertIsNone(result)

    def test_get_model_request_exception(self):
        """Test get_model handles request exception."""
        self.base_client.session.get.side_effect = requests.exceptions.RequestException(
            "Error"
        )

        result = self.manager.get_model("model1")

        self.assertIsNone(result)

    def test_get_model_json_decode_error(self):
        """Test get_model handles JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_response.raise_for_status = Mock()
        self.base_client.session.get.return_value = mock_response

        result = self.manager.get_model("model1")

        self.assertIsNone(result)


class TestModelManagerCRUD(unittest.TestCase):
    """Test CRUD operations in ModelManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = Mock(spec=BaseClient)
        self.base_client.base_url = "http://localhost:3000"
        self.base_client.session = Mock()
        self.base_client.json_headers = {"Authorization": "Bearer test_token"}
        self.manager = ModelManager(self.base_client, skip_initial_refresh=True)

    def test_create_model_request_exception(self):
        """Test create_model handles request exception."""
        self.base_client.session.post.side_effect = (
            requests.exceptions.RequestException("Error")
        )

        result = self.manager.create_model(model_id="new_model", name="New Model")

        self.assertIsNone(result)

    def test_create_model_json_decode_error(self):
        """Test create_model handles JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_response.raise_for_status = Mock()
        self.base_client.session.post.return_value = mock_response

        result = self.manager.create_model(model_id="new_model", name="New Model")

        self.assertIsNone(result)

    def test_update_model_request_exception(self):
        """Test update_model handles request exception."""
        self.base_client.session.post.side_effect = (
            requests.exceptions.RequestException("Error")
        )

        result = self.manager.update_model(model_id="model1", name="Updated Name")

        self.assertIsNone(result)

    def test_update_model_json_decode_error(self):
        """Test update_model handles JSON decode error."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_response.raise_for_status = Mock()
        self.base_client.session.post.return_value = mock_response

        result = self.manager.update_model(model_id="model1", name="Updated Name")

        self.assertIsNone(result)

    def test_delete_model_success(self):
        """Test delete_model successfully deletes model."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        self.base_client.session.delete.return_value = mock_response

        result = self.manager.delete_model("model1")

        self.assertTrue(result)

    def test_delete_model_request_exception(self):
        """Test delete_model handles request exception."""
        self.base_client.session.delete.side_effect = (
            requests.exceptions.RequestException("Error")
        )

        result = self.manager.delete_model("model1")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
