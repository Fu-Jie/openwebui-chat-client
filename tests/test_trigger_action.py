"""
Unit tests for trigger_action functionality.

Tests the trigger_action method in ChatManager and AsyncChatManager.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock


class TestTriggerAction(unittest.TestCase):
    """Tests for ChatManager.trigger_action method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_base_client = Mock()
        self.mock_base_client.session = self.mock_session
        self.mock_base_client.base_url = "http://localhost:3000"
        self.mock_base_client.json_headers = {"Content-Type": "application/json"}

    def test_trigger_action_success(self):
        """Test successful action trigger."""
        from openwebui_chat_client.modules.chat.manager import ChatManager

        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "action result"}
        self.mock_session.post.return_value = mock_response

        chat_manager = ChatManager(self.mock_base_client)
        result = chat_manager.trigger_action(
            action_id="test_action",
            chat_id="chat123",
            message_id="msg456",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.success, True)
        self.mock_session.post.assert_called_once()

    def test_trigger_action_with_chinese_id(self):
        """Test action trigger with Chinese action ID (URL encoding)."""
        from openwebui_chat_client.modules.chat.manager import ChatManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        self.mock_session.post.return_value = mock_response

        chat_manager = ChatManager(self.mock_base_client)
        result = chat_manager.trigger_action(
            action_id="异步上下文压缩",
            chat_id="chat123",
            message_id="msg456",
        )

        self.assertIsNotNone(result)
        # Verify URL encoding was applied
        call_args = self.mock_session.post.call_args
        self.assertIn("%E5%BC%82%E6%AD%A5", call_args[0][0])

    def test_trigger_action_with_params(self):
        """Test action trigger with additional parameters."""
        from openwebui_chat_client.modules.chat.manager import ChatManager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        self.mock_session.post.return_value = mock_response

        chat_manager = ChatManager(self.mock_base_client)
        result = chat_manager.trigger_action(
            action_id="test_action",
            chat_id="chat123",
            message_id="msg456",
            params={"extra_param": "value"},
        )

        self.assertIsNotNone(result)
        call_args = self.mock_session.post.call_args
        payload = call_args[1]["json"]
        self.assertEqual(payload["extra_param"], "value")

    def test_trigger_action_failure(self):
        """Test action trigger failure handling."""
        from openwebui_chat_client.modules.chat.manager import ChatManager

        self.mock_session.post.side_effect = Exception("Connection failed")

        chat_manager = ChatManager(self.mock_base_client)
        result = chat_manager.trigger_action(
            action_id="test_action",
            chat_id="chat123",
            message_id="msg456",
        )

        self.assertIsNone(result)

    def test_trigger_action_http_error(self):
        """Test action trigger with HTTP error response."""
        from openwebui_chat_client.modules.chat.manager import ChatManager
        from requests.exceptions import HTTPError

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("Not found")
        self.mock_session.post.return_value = mock_response

        chat_manager = ChatManager(self.mock_base_client)
        result = chat_manager.trigger_action(
            action_id="nonexistent_action",
            chat_id="chat123",
            message_id="msg456",
        )

        self.assertIsNone(result)


class TestAsyncTriggerAction(unittest.TestCase):
    """Tests for AsyncChatManager.trigger_action method."""

    def test_async_trigger_action_success(self):
        """Test successful async action trigger."""
        import asyncio

        async def run_test():
            from openwebui_chat_client.modules.async_.async_chat_manager import (
                AsyncChatManager,
            )

            mock_base_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"success": True}

            async def mock_make_request(*args, **kwargs):
                return mock_response

            mock_base_client._make_request = mock_make_request

            manager = AsyncChatManager(mock_base_client)
            result = await manager.trigger_action(
                action_id="test_action",
                chat_id="chat123",
                message_id="msg456",
            )

            self.assertIsNotNone(result)
            self.assertEqual(result.success, True)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
