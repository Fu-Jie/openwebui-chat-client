"""
Unit tests for get_chat functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock


class TestGetChat(unittest.TestCase):
    """Tests for ChatManager.get_chat method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock()
        self.mock_base_client = MagicMock()
        self.mock_base_client.session = self.mock_session
        self.mock_base_client.base_url = "http://localhost:3000"
        self.mock_base_client.json_headers = {"Content-Type": "application/json"}
        # Mock chat_object_from_server as a dict
        self.mock_base_client.chat_object_from_server = {}
        # Important: Set _parent_client to None to avoid delegation logic in ChatManager
        self.mock_base_client._parent_client = None

    def test_get_chat_success(self):
        """Test successful get_chat."""
        from openwebui_chat_client.modules.chat.manager import ChatManager

        # Setup mock response for _load_chat_details -> session.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chat": {"id": "chat123", "title": "Test Chat", "history": {"messages": {}}}
        }
        self.mock_session.get.return_value = mock_response

        chat_manager = ChatManager(self.mock_base_client)

        result = chat_manager.get_chat("chat123")

        self.assertIsNotNone(result)
        # result is a ChatDetails object
        self.assertEqual(result.chat.id, "chat123")
        self.mock_session.get.assert_called()

    def test_get_chat_failure(self):
        """Test get_chat failure."""
        from openwebui_chat_client.modules.chat.manager import ChatManager

        # Setup mock response for failure
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not Found")
        self.mock_session.get.return_value = mock_response

        chat_manager = ChatManager(self.mock_base_client)
        result = chat_manager.get_chat("nonexistent")

        self.assertIsNone(result)


class TestAsyncGetChat(unittest.TestCase):
    """Tests for AsyncChatManager.get_chat method."""

    def test_async_get_chat_success(self):
        """Test successful async get_chat."""
        import asyncio
        from openwebui_chat_client.modules.async_.async_chat_manager import AsyncChatManager

        async def run_test():
            mock_base_client = MagicMock()
            mock_base_client.chat_object_from_server = {"chat": {"id": "chat123"}}

            # Mock _load_chat_details to return True
            async def mock_load_chat_details(chat_id):
                return True

            manager = AsyncChatManager(mock_base_client)
            manager._load_chat_details = mock_load_chat_details

            result = await manager.get_chat("chat123")

            self.assertIsNotNone(result)
            # result is a ChatDetails object
            self.assertEqual(result.chat.id, "chat123")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
