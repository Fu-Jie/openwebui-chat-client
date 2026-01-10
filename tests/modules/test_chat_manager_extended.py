"""
Extended tests for ChatManager - focusing on core chat operations.

This test file covers:
- chat() method with various parameters
- parallel_chat() method
- stream_chat() method
- switch_chat_model() method
- update_chat_metadata() method
- get_chats_by_folder() method
- Helper methods for chat operations
"""

import json
import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

from openwebui_chat_client.modules.chat_manager import ChatManager


class TestChatManagerCoreOperations(unittest.TestCase):
    """Test core chat operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = MagicMock()
        self.base_client.base_url = "http://test.com"
        self.base_client.session = MagicMock()
        self.base_client.json_headers = {"Content-Type": "application/json"}
        self.base_client.default_model_id = "test-model"
        self.base_client.model_id = "test-model"
        self.base_client.chat_id = "test-chat-id"
        self.base_client._parent_client = None  # Disable parent client delegation
        self.base_client.chat_object_from_server = {
            "chat": {
                "id": "test-chat-id",
                "title": "Test Chat",
                "models": ["test-model"],
                "history": {"messages": {}, "currentId": None},
                "messages": [],
            }
        }
        self.manager = ChatManager(self.base_client)

    def test_chat_basic_success(self):
        """Test basic chat operation."""
        # Mock the internal methods
        self.manager._find_or_create_chat_by_title = MagicMock()
        self.manager._ask = MagicMock(
            return_value=("Test response", "msg-id", ["Follow up?"])
        )

        result = self.manager.chat(
            question="Hello", chat_title="Test Chat", enable_follow_up=True
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["response"], "Test response")
        self.assertEqual(result["message_id"], "msg-id")
        self.assertEqual(result["follow_ups"], ["Follow up?"])
        self.manager._find_or_create_chat_by_title.assert_called_once_with("Test Chat")

    def test_chat_with_folder(self):
        """Test chat with folder organization."""
        self.manager._find_or_create_chat_by_title = MagicMock()
        self.manager._ask = MagicMock(return_value=("Response", "msg-id", None))
        self.manager.get_folder_id_by_name = MagicMock(return_value="folder-id")
        self.manager.move_chat_to_folder = MagicMock()

        result = self.manager.chat(
            question="Hello", chat_title="Test Chat", folder_name="TestFolder"
        )

        self.assertIsNotNone(result)
        self.manager.get_folder_id_by_name.assert_called_once_with("TestFolder")
        self.manager.move_chat_to_folder.assert_called_once_with(
            "test-chat-id", "folder-id"
        )

    def test_chat_with_tags(self):
        """Test chat with tags."""
        self.manager._find_or_create_chat_by_title = MagicMock()
        self.manager._ask = MagicMock(return_value=("Response", "msg-id", None))
        self.manager.set_chat_tags = MagicMock()

        result = self.manager.chat(
            question="Hello", chat_title="Test Chat", tags=["tag1", "tag2"]
        )

        self.assertIsNotNone(result)
        self.manager.set_chat_tags.assert_called_once_with(
            "test-chat-id", ["tag1", "tag2"]
        )

    def test_chat_with_auto_tagging(self):
        """Test chat with auto-tagging enabled."""
        self.manager._find_or_create_chat_by_title = MagicMock()
        self.manager._ask = MagicMock(return_value=("Response", "msg-id", None))
        self.manager._build_linear_history_for_api = MagicMock(return_value=[])
        self.manager._get_tags = MagicMock(return_value=["auto-tag1", "auto-tag2"])
        self.manager.set_chat_tags = MagicMock()

        result = self.manager.chat(
            question="Hello", chat_title="Test Chat", enable_auto_tagging=True
        )

        self.assertIsNotNone(result)
        self.assertIn("suggested_tags", result)
        self.assertEqual(result["suggested_tags"], ["auto-tag1", "auto-tag2"])
        self.manager._get_tags.assert_called_once()

    def test_chat_with_auto_titling(self):
        """Test chat with auto-titling enabled."""
        self.manager._find_or_create_chat_by_title = MagicMock()
        self.manager._ask = MagicMock(return_value=("Response", "msg-id", None))
        self.manager._build_linear_history_for_api = MagicMock(return_value=[])
        self.manager._get_title = MagicMock(return_value="Auto Generated Title")
        self.manager.rename_chat = MagicMock()

        result = self.manager.chat(
            question="Hello", chat_title="Test Chat", enable_auto_titling=True
        )

        self.assertIsNotNone(result)
        self.assertIn("suggested_title", result)
        self.assertEqual(result["suggested_title"], "Auto Generated Title")
        self.manager._get_title.assert_called_once()

    def test_chat_no_chat_object(self):
        """Test chat when chat object is not loaded."""
        self.base_client.chat_object_from_server = None
        self.manager._find_or_create_chat_by_title = MagicMock()

        result = self.manager.chat(question="Hello", chat_title="Test Chat")

        self.assertIsNone(result)

    def test_chat_no_chat_id(self):
        """Test chat when chat_id is not set."""
        self.base_client.chat_id = None
        self.manager._find_or_create_chat_by_title = MagicMock()

        result = self.manager.chat(question="Hello", chat_title="Test Chat")

        self.assertIsNone(result)

    def test_chat_ask_returns_none(self):
        """Test chat when _ask returns None."""
        self.manager._find_or_create_chat_by_title = MagicMock()
        self.manager._ask = MagicMock(return_value=(None, None, None))

        result = self.manager.chat(question="Hello", chat_title="Test Chat")

        self.assertIsNone(result)


class TestChatManagerParallelChat(unittest.TestCase):
    """Test parallel chat operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = MagicMock()
        self.base_client.base_url = "http://test.com"
        self.base_client.session = MagicMock()
        self.base_client.json_headers = {"Content-Type": "application/json"}
        self.base_client.default_model_id = "test-model"
        self.base_client.model_id = "test-model"
        self.base_client.chat_id = "test-chat-id"
        self.base_client.chat_object_from_server = {
            "chat": {
                "id": "test-chat-id",
                "title": "Test Chat",
                "models": ["model1", "model2"],
                "history": {"messages": {}, "currentId": None},
                "messages": [],
            }
        }
        self.manager = ChatManager(self.base_client)

    def test_parallel_chat_empty_model_ids(self):
        """Test parallel_chat with empty model_ids list."""
        result = self.manager.parallel_chat(
            question="Hello", chat_title="Test Chat", model_ids=[]
        )

        self.assertIsNone(result)

    def test_parallel_chat_no_chat_object(self):
        """Test parallel_chat when chat object is not loaded."""
        self.base_client.chat_object_from_server = None
        self.manager._find_or_create_chat_by_title = MagicMock()

        result = self.manager.parallel_chat(
            question="Hello", chat_title="Test Chat", model_ids=["model1", "model2"]
        )

        self.assertIsNone(result)

    def test_parallel_chat_no_chat_id(self):
        """Test parallel_chat when chat_id is not set."""
        self.base_client.chat_id = None
        self.manager._find_or_create_chat_by_title = MagicMock()

        result = self.manager.parallel_chat(
            question="Hello", chat_title="Test Chat", model_ids=["model1", "model2"]
        )

        self.assertIsNone(result)


class TestChatManagerSwitchModel(unittest.TestCase):
    """Test model switching operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = MagicMock()
        self.base_client.base_url = "http://test.com"
        self.base_client.session = MagicMock()
        self.base_client.json_headers = {"Content-Type": "application/json"}
        self.base_client.default_model_id = "test-model"
        self.base_client.model_id = "test-model"
        self.base_client.chat_id = "test-chat-id"
        self.base_client.chat_object_from_server = {
            "chat": {
                "id": "test-chat-id",
                "title": "Test Chat",
                "models": ["old-model"],
                "history": {"messages": {}, "currentId": None},
            }
        }
        self.base_client._parent_client = None
        self.manager = ChatManager(self.base_client)

    def test_switch_chat_model_empty_chat_id(self):
        """Test switch_chat_model with empty chat_id."""
        result = self.manager.switch_chat_model("", "new-model")

        self.assertFalse(result)

    def test_switch_chat_model_empty_model_ids(self):
        """Test switch_chat_model with empty model_ids."""
        result = self.manager.switch_chat_model("test-chat-id", [])

        self.assertFalse(result)

    def test_switch_chat_model_string_model_id(self):
        """Test switch_chat_model with string model_id."""
        self.manager._load_chat_details = MagicMock(return_value=True)
        self.manager._update_remote_chat = MagicMock(return_value=True)

        result = self.manager.switch_chat_model("test-chat-id", "new-model")

        self.assertTrue(result)
        self.assertEqual(
            self.base_client.chat_object_from_server["chat"]["models"], ["new-model"]
        )

    def test_switch_chat_model_same_model(self):
        """Test switch_chat_model when switching to same model."""
        self.base_client.chat_object_from_server["chat"]["models"] = ["test-model"]
        self.manager._load_chat_details = MagicMock(return_value=True)

        result = self.manager.switch_chat_model("test-chat-id", ["test-model"])

        self.assertTrue(result)

    def test_switch_chat_model_load_fails(self):
        """Test switch_chat_model when loading chat details fails."""
        self.manager._load_chat_details = MagicMock(return_value=False)

        result = self.manager.switch_chat_model("test-chat-id", "new-model")

        self.assertFalse(result)

    def test_switch_chat_model_update_fails(self):
        """Test switch_chat_model when updating remote chat fails."""
        self.manager._load_chat_details = MagicMock(return_value=True)
        self.manager._update_remote_chat = MagicMock(return_value=False)

        result = self.manager.switch_chat_model("test-chat-id", "new-model")

        self.assertFalse(result)


class TestChatManagerUpdateMetadata(unittest.TestCase):
    """Test chat metadata update operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = MagicMock()
        self.manager = ChatManager(self.base_client)

    def test_update_chat_metadata_empty_chat_id(self):
        """Test update_chat_metadata with empty chat_id."""
        result = self.manager.update_chat_metadata("", title="New Title")

        self.assertFalse(result)

    def test_update_chat_metadata_title_only(self):
        """Test update_chat_metadata with title only."""
        self.manager.rename_chat = MagicMock(return_value=True)

        result = self.manager.update_chat_metadata("test-chat-id", title="New Title")

        self.assertTrue(result)
        self.manager.rename_chat.assert_called_once_with("test-chat-id", "New Title")

    def test_update_chat_metadata_tags_only(self):
        """Test update_chat_metadata with tags only."""
        self.manager.set_chat_tags = MagicMock()

        result = self.manager.update_chat_metadata(
            "test-chat-id", tags=["tag1", "tag2"]
        )

        self.assertTrue(result)
        self.manager.set_chat_tags.assert_called_once_with(
            "test-chat-id", ["tag1", "tag2"]
        )

    def test_update_chat_metadata_folder_only(self):
        """Test update_chat_metadata with folder only."""
        self.manager.get_folder_id_by_name = MagicMock(return_value="folder-id")
        self.manager.move_chat_to_folder = MagicMock()

        result = self.manager.update_chat_metadata(
            "test-chat-id", folder_name="TestFolder"
        )

        self.assertTrue(result)
        self.manager.move_chat_to_folder.assert_called_once_with(
            "test-chat-id", "folder-id"
        )

    def test_update_chat_metadata_all_parameters(self):
        """Test update_chat_metadata with all parameters."""
        self.manager.rename_chat = MagicMock(return_value=True)
        self.manager.set_chat_tags = MagicMock()
        self.manager.get_folder_id_by_name = MagicMock(return_value="folder-id")
        self.manager.move_chat_to_folder = MagicMock()

        result = self.manager.update_chat_metadata(
            "test-chat-id",
            title="New Title",
            tags=["tag1"],
            folder_name="TestFolder",
        )

        self.assertTrue(result)
        self.manager.rename_chat.assert_called_once()
        self.manager.set_chat_tags.assert_called_once()
        self.manager.move_chat_to_folder.assert_called_once()

    def test_update_chat_metadata_rename_fails(self):
        """Test update_chat_metadata when rename fails."""
        self.manager.rename_chat = MagicMock(return_value=False)

        result = self.manager.update_chat_metadata("test-chat-id", title="New Title")

        self.assertFalse(result)

    def test_update_chat_metadata_tags_exception(self):
        """Test update_chat_metadata when set_chat_tags raises exception."""
        self.manager.set_chat_tags = MagicMock(side_effect=Exception("Tag error"))

        result = self.manager.update_chat_metadata(
            "test-chat-id", tags=["tag1", "tag2"]
        )

        self.assertFalse(result)

    def test_update_chat_metadata_folder_exception(self):
        """Test update_chat_metadata when folder operations raise exception."""
        self.manager.get_folder_id_by_name = MagicMock(
            side_effect=Exception("Folder error")
        )

        result = self.manager.update_chat_metadata(
            "test-chat-id", folder_name="TestFolder"
        )

        self.assertFalse(result)


class TestChatManagerGetChatsByFolder(unittest.TestCase):
    """Test get_chats_by_folder operation."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = MagicMock()
        self.base_client.base_url = "http://test.com"
        self.base_client.session = MagicMock()
        self.base_client.json_headers = {"Content-Type": "application/json"}
        self.manager = ChatManager(self.base_client)

    def test_get_chats_by_folder_success(self):
        """Test get_chats_by_folder with successful response."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": "chat1", "title": "Chat 1"},
            {"id": "chat2", "title": "Chat 2"},
        ]
        self.base_client.session.get.return_value = mock_response

        result = self.manager.get_chats_by_folder("folder-id")

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.base_client.session.get.assert_called_once()

    def test_get_chats_by_folder_http_error(self):
        """Test get_chats_by_folder with HTTP error."""
        import requests

        self.base_client.session.get.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )

        result = self.manager.get_chats_by_folder("folder-id")

        self.assertIsNone(result)

    def test_get_chats_by_folder_connection_error(self):
        """Test get_chats_by_folder with connection error."""
        import requests

        self.base_client.session.get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        result = self.manager.get_chats_by_folder("folder-id")

        self.assertIsNone(result)


class TestChatManagerHelperMethods(unittest.TestCase):
    """Test helper methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_client = MagicMock()
        self.base_client.base_url = "http://test.com"
        self.base_client.session = MagicMock()
        self.base_client.json_headers = {"Content-Type": "application/json"}
        self.base_client.chat_id = "test-chat-id"
        self.base_client.chat_object_from_server = {
            "chat": {
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
                    },
                    "currentId": "msg2",
                }
            }
        }
        self.manager = ChatManager(self.base_client)

    def test_extract_json_from_content_plain_json(self):
        """Test _extract_json_from_content with plain JSON."""
        content = '{"key": "value"}'
        result = self.manager._extract_json_from_content(content)

        self.assertIsNotNone(result)
        self.assertEqual(result["key"], "value")

    def test_extract_json_from_content_markdown_json(self):
        """Test _extract_json_from_content with markdown code block."""
        content = '```json\n{"key": "value"}\n```'
        result = self.manager._extract_json_from_content(content)

        self.assertIsNotNone(result)
        self.assertEqual(result["key"], "value")

    def test_extract_json_from_content_markdown_no_lang(self):
        """Test _extract_json_from_content with markdown code block without language."""
        content = '```\n{"key": "value"}\n```'
        result = self.manager._extract_json_from_content(content)

        self.assertIsNotNone(result)
        self.assertEqual(result["key"], "value")

    def test_extract_json_from_content_single_backticks(self):
        """Test _extract_json_from_content with single backticks."""
        content = '`{"key": "value"}`'
        result = self.manager._extract_json_from_content(content)

        self.assertIsNotNone(result)
        self.assertEqual(result["key"], "value")

    def test_extract_json_from_content_embedded_json(self):
        """Test _extract_json_from_content with JSON embedded in text."""
        content = 'Here is the result: {"key": "value"} and more text'
        result = self.manager._extract_json_from_content(content)

        self.assertIsNotNone(result)
        self.assertEqual(result["key"], "value")

    def test_extract_json_from_content_empty(self):
        """Test _extract_json_from_content with empty content."""
        result = self.manager._extract_json_from_content("")

        self.assertIsNone(result)

    def test_extract_json_from_content_invalid(self):
        """Test _extract_json_from_content with invalid JSON."""
        content = "This is not JSON at all"
        result = self.manager._extract_json_from_content(content)

        self.assertIsNone(result)

    def test_parse_todo_list_valid(self):
        """Test _parse_todo_list with valid todo list."""
        content = """Todo List:
- [x] Task 1
- [@] Task 2
- [ ] Task 3
"""
        result = self.manager._parse_todo_list(content)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["status"], "completed")
        self.assertEqual(result[1]["status"], "in_progress")
        self.assertEqual(result[2]["status"], "pending")

    def test_parse_todo_list_no_list(self):
        """Test _parse_todo_list with no todo list."""
        content = "Just some regular text"
        result = self.manager._parse_todo_list(content)

        self.assertIsNone(result)

    def test_detect_options_in_response_valid(self):
        """Test _detect_options_in_response with valid options."""
        response = """**Options:**
1. [Option A]: First approach
2. [Option B]: Second approach
3. [Option C]: Third approach
"""
        result = self.manager._detect_options_in_response(response)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["number"], "1")
        self.assertEqual(result[0]["label"], "Option A")

    def test_detect_options_in_response_no_options(self):
        """Test _detect_options_in_response with no options."""
        response = "Just regular text without options"
        result = self.manager._detect_options_in_response(response)

        self.assertIsNone(result)

    def test_detect_options_in_response_single_option(self):
        """Test _detect_options_in_response with only one option."""
        response = """**Options:**
1. [Option A]: Only one option
"""
        result = self.manager._detect_options_in_response(response)

        self.assertIsNone(result)  # Need at least 2 options


if __name__ == "__main__":
    unittest.main()
