"""
Unit tests for get_functions functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock


class TestGetFunctions(unittest.TestCase):
    """Tests for ChatManager.get_functions method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock()
        self.mock_base_client = MagicMock()
        self.mock_base_client.session = self.mock_session
        self.mock_base_client.base_url = "http://localhost:3000"
        self.mock_base_client.json_headers = {"Content-Type": "application/json"}
        # Important: Set _parent_client to None to avoid delegation logic in ChatManager
        self.mock_base_client._parent_client = None

    def test_get_functions_success(self):
        """Test successful get_functions."""
        from openwebui_chat_client.modules.chat_manager import ChatManager

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "func1", "name": "Function 1"},
            {"id": "func2", "name": "Function 2"},
        ]
        self.mock_session.get.return_value = mock_response

        chat_manager = ChatManager(self.mock_base_client)

        result = chat_manager.get_functions()

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        # result[0] is a Function object
        self.assertEqual(result[0].id, "func1")
        self.mock_session.get.assert_called_with(
            "http://localhost:3000/api/v1/functions/",
            headers={"Content-Type": "application/json"},
        )

    def test_get_functions_failure(self):
        """Test get_functions failure."""
        from openwebui_chat_client.modules.chat_manager import ChatManager
        import requests

        # Setup mock response for failure
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Internal Server Error"
        )
        self.mock_session.get.return_value = mock_response

        chat_manager = ChatManager(self.mock_base_client)
        result = chat_manager.get_functions()

        self.assertIsNone(result)


class TestAsyncGetFunctions(unittest.TestCase):
    """Tests for AsyncChatManager.get_functions method."""

    def test_async_get_functions_success(self):
        """Test successful async get_functions."""
        import asyncio
        from openwebui_chat_client.modules.async_chat_manager import AsyncChatManager

        async def run_test():
            mock_base_client = MagicMock()

            # Mock _get_json_response
            async def mock_get_json_response(method, url, **kwargs):
                return [{"id": "func1", "name": "Function 1"}]

            mock_base_client._get_json_response = mock_get_json_response

            manager = AsyncChatManager(mock_base_client)

            result = await manager.get_functions()

            self.assertIsNotNone(result)
            self.assertEqual(len(result), 1)
            # result[0] is a Function object
            self.assertEqual(result[0].id, "func1")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
