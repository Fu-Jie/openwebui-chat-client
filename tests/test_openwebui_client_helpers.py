"""
Tests for OpenWebUIClient helper methods.

This test file focuses on testing internal helper methods in the main
OpenWebUIClient class that handle chat operations, history building, and API interactions.
"""

import json
import unittest
from unittest.mock import MagicMock, Mock, patch, call
from typing import Dict, Any, List
import requests

from openwebui_chat_client import OpenWebUIClient


class TestOpenWebUIClientHelpers(unittest.TestCase):
    """Test helper methods in OpenWebUIClient."""

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

    def test_build_linear_history_for_storage(self):
        """Test _build_linear_history_for_storage builds correct history."""
        chat_core = {
            "history": {
                "messages": {
                    "msg1": {
                        "id": "msg1",
                        "role": "user",
                        "content": "Hello",
                        "parentId": None,
                    },
                    "msg2": {
                        "id": "msg2",
                        "role": "assistant",
                        "content": "Hi",
                        "parentId": "msg1",
                    },
                    "msg3": {
                        "id": "msg3",
                        "role": "user",
                        "content": "How are you?",
                        "parentId": "msg2",
                    },
                }
            }
        }

        result = self.client._build_linear_history_for_storage(chat_core, "msg3")

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["id"], "msg1")
        self.assertEqual(result[1]["id"], "msg2")
        self.assertEqual(result[2]["id"], "msg3")

    def test_build_linear_history_for_storage_empty(self):
        """Test _build_linear_history_for_storage with empty history."""
        chat_core = {"history": {"messages": {}}}

        result = self.client._build_linear_history_for_storage(chat_core, "nonexistent")

        self.assertEqual(len(result), 0)

    @patch("requests.Session.post")
    def test_update_remote_chat_success(self, mock_post):
        """Test _update_remote_chat successfully updates chat."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        self.client.chat_id = "test_chat_123"
        self.client.chat_object_from_server = {
            "chat": {"id": "test_chat_123", "title": "Test Chat"}
        }

        result = self.client._update_remote_chat()

        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch("requests.Session.post")
    def test_update_remote_chat_failure(self, mock_post):
        """Test _update_remote_chat handles failure."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        self.client.chat_id = "test_chat_123"
        self.client.chat_object_from_server = {
            "chat": {"id": "test_chat_123", "title": "Test Chat"}
        }

        result = self.client._update_remote_chat()

        self.assertFalse(result)

    @patch("requests.Session.get")
    def test_load_chat_details_success(self, mock_get):
        """Test _load_chat_details successfully loads chat."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "test_chat_123",
            "chat": {"title": "Test Chat"},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client._load_chat_details("test_chat_123")

        self.assertTrue(result)
        self.assertEqual(self.client.chat_object_from_server["id"], "test_chat_123")

    @patch("requests.Session.get")
    def test_load_chat_details_none_response(self, mock_get):
        """Test _load_chat_details handles None response."""
        mock_response = Mock()
        mock_response.json.return_value = None
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client._load_chat_details("test_chat_123")

        self.assertFalse(result)

    @patch("requests.Session.get")
    def test_load_chat_details_empty_response(self, mock_get):
        """Test _load_chat_details handles empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client._load_chat_details("test_chat_123")

        self.assertFalse(result)

    @patch("requests.Session.get")
    def test_load_chat_details_request_exception(self, mock_get):
        """Test _load_chat_details handles request exception."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = self.client._load_chat_details("test_chat_123")

        self.assertFalse(result)

    @patch("requests.Session.get")
    def test_search_latest_chat_by_title_success(self, mock_get):
        """Test _search_latest_chat_by_title finds latest chat."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "chat1", "title": "Test Chat", "updated_at": 1000},
            {"id": "chat2", "title": "Test Chat", "updated_at": 2000},
            {"id": "chat3", "title": "Other Chat", "updated_at": 3000},
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client._search_latest_chat_by_title("Test Chat")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "chat2")  # Latest with matching title

    @patch("requests.Session.get")
    def test_search_latest_chat_by_title_not_found(self, mock_get):
        """Test _search_latest_chat_by_title when no match found."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "chat1", "title": "Other Chat", "updated_at": 1000},
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client._search_latest_chat_by_title("Test Chat")

        self.assertIsNone(result)

    @patch("requests.Session.get")
    def test_search_latest_chat_by_title_empty_list(self, mock_get):
        """Test _search_latest_chat_by_title with empty results."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client._search_latest_chat_by_title("Test Chat")

        self.assertIsNone(result)

    @patch("requests.Session.get")
    def test_search_latest_chat_by_title_exception(self, mock_get):
        """Test _search_latest_chat_by_title handles exception."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = self.client._search_latest_chat_by_title("Test Chat")

        self.assertIsNone(result)

    @patch("requests.Session.post")
    def test_create_new_chat_success(self, mock_post):
        """Test _create_new_chat successfully creates chat."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "new_chat_123"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client._create_new_chat("New Chat")

        self.assertEqual(result, "new_chat_123")

    @patch("requests.Session.post")
    def test_create_new_chat_no_id(self, mock_post):
        """Test _create_new_chat when response has no ID."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client._create_new_chat("New Chat")

        self.assertIsNone(result)

    @patch("requests.Session.post")
    def test_create_new_chat_exception(self, mock_post):
        """Test _create_new_chat handles exception."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        result = self.client._create_new_chat("New Chat")

        self.assertIsNone(result)

    @patch("requests.Session.get")
    def test_get_chat_details_success(self, mock_get):
        """Test _get_chat_details successfully retrieves details."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "chat123", "title": "Test"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client._get_chat_details("chat123")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "chat123")

    @patch("requests.Session.get")
    def test_get_chat_details_exception(self, mock_get):
        """Test _get_chat_details handles exception."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = self.client._get_chat_details("chat123")

        self.assertIsNone(result)

    def test_is_placeholder_message_true(self):
        """Test _is_placeholder_message identifies placeholder."""
        message = {"content": "", "done": False}

        result = self.client._is_placeholder_message(message)

        self.assertTrue(result)

    def test_is_placeholder_message_with_content(self):
        """Test _is_placeholder_message with content."""
        message = {"content": "Hello", "done": False}

        result = self.client._is_placeholder_message(message)

        self.assertFalse(result)

    def test_is_placeholder_message_done(self):
        """Test _is_placeholder_message when done is True."""
        message = {"content": "", "done": True}

        result = self.client._is_placeholder_message(message)

        self.assertFalse(result)

    def test_is_placeholder_message_whitespace(self):
        """Test _is_placeholder_message with whitespace content."""
        message = {"content": "   ", "done": False}

        result = self.client._is_placeholder_message(message)

        self.assertTrue(result)


class TestExtractJsonFromContent(unittest.TestCase):
    """Test _extract_json_from_content method."""

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

    def test_extract_json_plain(self):
        """Test extracting plain JSON."""
        content = '{"key": "value", "number": 42}'
        result = self.client._extract_json_from_content(content)

        self.assertEqual(result, {"key": "value", "number": 42})

    def test_extract_json_from_markdown_json_block(self):
        """Test extracting JSON from markdown ```json block."""
        content = '```json\n{"key": "value"}\n```'
        result = self.client._extract_json_from_content(content)

        self.assertEqual(result, {"key": "value"})

    def test_extract_json_from_markdown_code_block(self):
        """Test extracting JSON from markdown ``` block."""
        content = '```\n{"key": "value"}\n```'
        result = self.client._extract_json_from_content(content)

        self.assertEqual(result, {"key": "value"})

    def test_extract_json_from_backticks(self):
        """Test extracting JSON from single backticks."""
        content = '`{"key": "value"}`'
        result = self.client._extract_json_from_content(content)

        self.assertEqual(result, {"key": "value"})

    def test_extract_json_with_surrounding_text(self):
        """Test extracting JSON with surrounding text."""
        content = 'Here is the result: {"key": "value"} and more text'
        result = self.client._extract_json_from_content(content)

        self.assertEqual(result, {"key": "value"})

    def test_extract_json_empty_content(self):
        """Test extracting JSON from empty content."""
        result = self.client._extract_json_from_content("")

        self.assertIsNone(result)

    def test_extract_json_none_content(self):
        """Test extracting JSON from None content."""
        result = self.client._extract_json_from_content(None)

        self.assertIsNone(result)

    def test_extract_json_invalid_json(self):
        """Test extracting JSON from invalid JSON."""
        content = "This is not JSON at all"
        result = self.client._extract_json_from_content(content)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
