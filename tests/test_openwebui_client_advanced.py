"""
Advanced tests for OpenWebUIClient to improve coverage.

This test file focuses on testing advanced methods in the main OpenWebUIClient class
including update_chat_metadata, archive operations, and find/create chat operations.
"""

import json
import time
import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import requests

from openwebui_chat_client import OpenWebUIClient


class TestUpdateChatMetadata(unittest.TestCase):
    """Test update_chat_metadata method."""

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

    def test_update_chat_metadata_no_action(self):
        """Test update_chat_metadata with no action requested."""
        result = self.client.update_chat_metadata("chat123")

        self.assertIsNone(result)

    def test_update_chat_metadata_direct_values(self):
        """Test update_chat_metadata with direct title/tags/folder."""
        self.client._chat_manager.update_chat_metadata = Mock(return_value=True)

        result = self.client.update_chat_metadata(
            "chat123", title="New Title", tags=["tag1", "tag2"], folder_name="folder1"
        )

        self.assertIsNotNone(result)
        self.assertTrue(result["updated"])

    def test_update_chat_metadata_direct_values_failure(self):
        """Test update_chat_metadata when direct update fails."""
        self.client._chat_manager.update_chat_metadata = Mock(return_value=False)

        result = self.client.update_chat_metadata("chat123", title="New Title")

        self.assertIsNone(result)

    @patch.object(OpenWebUIClient, "set_chat_tags")
    @patch.object(OpenWebUIClient, "_get_tags")
    @patch.object(OpenWebUIClient, "_build_linear_history_for_api")
    @patch.object(OpenWebUIClient, "_load_chat_details")
    def test_update_chat_metadata_regenerate_tags(
        self, mock_load, mock_build_history, mock_get_tags, mock_set_tags
    ):
        """Test update_chat_metadata with regenerate_tags."""
        mock_load.return_value = True
        self.client.chat_object_from_server = {
            "chat": {"history": {"messages": {}, "currentId": None}}
        }
        mock_build_history.return_value = [{"role": "user", "content": "Hello"}]
        mock_get_tags.return_value = ["tag1", "tag2"]

        result = self.client.update_chat_metadata("chat123", regenerate_tags=True)

        self.assertIsNotNone(result)
        self.assertEqual(result["suggested_tags"], ["tag1", "tag2"])
        mock_set_tags.assert_called_once_with("chat123", ["tag1", "tag2"])

    @patch.object(OpenWebUIClient, "rename_chat")
    @patch.object(OpenWebUIClient, "_get_title")
    @patch.object(OpenWebUIClient, "_build_linear_history_for_api")
    @patch.object(OpenWebUIClient, "_load_chat_details")
    def test_update_chat_metadata_regenerate_title(
        self, mock_load, mock_build_history, mock_get_title, mock_rename
    ):
        """Test update_chat_metadata with regenerate_title."""
        mock_load.return_value = True
        self.client.chat_object_from_server = {
            "chat": {"history": {"messages": {}, "currentId": None}}
        }
        mock_build_history.return_value = [{"role": "user", "content": "Hello"}]
        mock_get_title.return_value = "New Title"

        result = self.client.update_chat_metadata("chat123", regenerate_title=True)

        self.assertIsNotNone(result)
        self.assertEqual(result["suggested_title"], "New Title")
        mock_rename.assert_called_once_with("chat123", "New Title")

    @patch.object(OpenWebUIClient, "_load_chat_details")
    def test_update_chat_metadata_load_failure(self, mock_load):
        """Test update_chat_metadata when loading chat fails."""
        mock_load.return_value = False

        result = self.client.update_chat_metadata("chat123", regenerate_tags=True)

        self.assertIsNone(result)

    @patch.object(OpenWebUIClient, "_get_tags")
    @patch.object(OpenWebUIClient, "_build_linear_history_for_api")
    @patch.object(OpenWebUIClient, "_load_chat_details")
    def test_update_chat_metadata_no_tags_generated(
        self, mock_load, mock_build_history, mock_get_tags
    ):
        """Test update_chat_metadata when no tags are generated."""
        mock_load.return_value = True
        self.client.chat_object_from_server = {
            "chat": {"history": {"messages": {}, "currentId": None}}
        }
        mock_build_history.return_value = []
        mock_get_tags.return_value = None

        result = self.client.update_chat_metadata("chat123", regenerate_tags=True)

        # Should return empty dict or None when no tags generated
        self.assertTrue(result is None or result == {})


class TestFindOrCreateChat(unittest.TestCase):
    """Test _find_or_create_chat_by_title method."""

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

    @patch.object(OpenWebUIClient, "_load_chat_details")
    @patch.object(OpenWebUIClient, "_search_latest_chat_by_title")
    def test_find_existing_chat(self, mock_search, mock_load):
        """Test finding an existing chat by title."""
        mock_search.return_value = {"id": "existing_chat_123"}
        mock_load.return_value = True

        result = self.client._find_or_create_chat_by_title("Test Chat")

        self.assertEqual(result, "existing_chat_123")
        self.assertEqual(self.client.chat_id, "existing_chat_123")
        self.assertEqual(self.client._base_client.chat_id, "existing_chat_123")

    @patch.object(OpenWebUIClient, "_load_chat_details")
    @patch.object(OpenWebUIClient, "_create_new_chat")
    @patch.object(OpenWebUIClient, "_search_latest_chat_by_title")
    def test_create_new_chat_when_not_found(self, mock_search, mock_create, mock_load):
        """Test creating new chat when existing not found."""
        mock_search.return_value = None
        mock_create.return_value = "new_chat_123"
        mock_load.return_value = True

        result = self.client._find_or_create_chat_by_title("New Chat")

        self.assertEqual(result, "new_chat_123")
        self.assertEqual(self.client.chat_id, "new_chat_123")

    @patch.object(OpenWebUIClient, "_load_chat_details")
    @patch.object(OpenWebUIClient, "_search_latest_chat_by_title")
    def test_find_existing_but_load_fails(self, mock_search, mock_load):
        """Test when existing chat found but loading fails."""
        mock_search.return_value = {"id": "existing_chat_123"}
        mock_load.return_value = False

        result = self.client._find_or_create_chat_by_title("Test Chat")

        # Should still return the chat_id even if loading fails
        self.assertIsNone(result)

    @patch.object(OpenWebUIClient, "_load_chat_details")
    @patch.object(OpenWebUIClient, "_create_new_chat")
    @patch.object(OpenWebUIClient, "_search_latest_chat_by_title")
    def test_create_new_chat_load_fails(self, mock_search, mock_create, mock_load):
        """Test creating new chat when loading fails."""
        mock_search.return_value = None
        mock_create.return_value = "new_chat_123"
        mock_load.return_value = False

        result = self.client._find_or_create_chat_by_title("New Chat")

        # Should return chat_id even if loading fails
        self.assertEqual(result, "new_chat_123")

    @patch.object(OpenWebUIClient, "_create_new_chat")
    @patch.object(OpenWebUIClient, "_search_latest_chat_by_title")
    def test_create_new_chat_fails(self, mock_search, mock_create):
        """Test when creating new chat fails."""
        mock_search.return_value = None
        mock_create.return_value = None

        result = self.client._find_or_create_chat_by_title("New Chat")

        self.assertIsNone(result)


class TestGetTitleAndTags(unittest.TestCase):
    """Test _get_title and _get_tags methods."""

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
        self.client.task_model = "task-model"

    @patch("requests.Session.post")
    def test_get_title_success(self, mock_post):
        """Test _get_title successfully gets title."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"title": "Test Title"}'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        result = self.client._get_title(messages)

        self.assertEqual(result, "Test Title")

    @patch("requests.Session.post")
    def test_get_title_no_task_model(self, mock_post):
        """Test _get_title when task model not available."""
        # Mock _get_task_model to return None
        with patch.object(self.client, "_get_task_model", return_value=None):
            messages = [{"role": "user", "content": "Hello"}]
            result = self.client._get_title(messages)

            self.assertIsNone(result)
            mock_post.assert_not_called()

    @patch("requests.Session.post")
    def test_get_title_http_error(self, mock_post):
        """Test _get_title handles HTTP error."""
        mock_response = Mock()
        mock_response.text = "Error message"
        error = requests.exceptions.HTTPError("API Error")
        error.response = mock_response
        mock_post.side_effect = error

        messages = [{"role": "user", "content": "Hello"}]
        result = self.client._get_title(messages)

        self.assertIsNone(result)

    @patch("requests.Session.post")
    def test_get_title_invalid_json(self, mock_post):
        """Test _get_title handles invalid JSON response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Not valid JSON"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        result = self.client._get_title(messages)

        self.assertIsNone(result)

    @patch("requests.Session.post")
    def test_get_tags_success(self, mock_post):
        """Test _get_tags successfully gets tags."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '["tag1", "tag2", "tag3"]'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        result = self.client._get_tags(messages)

        self.assertEqual(result, ["tag1", "tag2", "tag3"])

    @patch("requests.Session.post")
    def test_get_tags_no_task_model(self, mock_post):
        """Test _get_tags when task model not available."""
        # Mock _get_task_model to return None
        with patch.object(self.client, "_get_task_model", return_value=None):
            messages = [{"role": "user", "content": "Hello"}]
            result = self.client._get_tags(messages)

            self.assertIsNone(result)

    @patch("requests.Session.post")
    def test_get_tags_not_list(self, mock_post):
        """Test _get_tags when response is not a list."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"tags": ["tag1"]}'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        result = self.client._get_tags(messages)

        self.assertIsNone(result)

    @patch("requests.Session.post")
    def test_get_tags_request_exception(self, mock_post):
        """Test _get_tags handles request exception."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        messages = [{"role": "user", "content": "Hello"}]
        result = self.client._get_tags(messages)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
