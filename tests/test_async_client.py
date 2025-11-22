"""
Unit tests for AsyncOpenWebUIClient and async managers.
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch
import httpx
from openwebui_chat_client import AsyncOpenWebUIClient

class TestAsyncOpenWebUIClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.base_url = "http://localhost:3000"
        self.token = "test_token"
        self.default_model_id = "test-model"
        self.client = AsyncOpenWebUIClient(self.base_url, self.token, self.default_model_id)

        # Mock the internal httpx client
        self.mock_httpx_client = AsyncMock(spec=httpx.AsyncClient)
        self.client._base_client.client = self.mock_httpx_client

    async def asyncTearDown(self):
        await self.client.close()

    async def test_initialization(self):
        self.assertIsInstance(self.client, AsyncOpenWebUIClient)
        self.assertEqual(self.client._base_client.base_url, self.base_url)

    async def test_get_users(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "user1", "name": "User 1"}]
        self.mock_httpx_client.get.return_value = mock_response

        users = await self.client.get_users()

        self.assertIsNotNone(users)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["id"], "user1")
        self.mock_httpx_client.get.assert_called_once()

    async def test_list_chats(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "chat1", "title": "Chat 1"}]
        self.mock_httpx_client.get.return_value = mock_response

        chats = await self.client.list_chats()

        self.assertIsNotNone(chats)
        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0]["id"], "chat1")

    async def test_chat(self):
        # Mock search response (chat not found)
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = []

        # Mock create response
        create_response = Mock()
        create_response.status_code = 200
        create_response.json.return_value = {"id": "new_chat_id"}

        # Mock load details response
        details_response = Mock()
        details_response.status_code = 200
        details_response.json.return_value = {
            "id": "new_chat_id",
            "chat": {
                "history": {"messages": {}, "currentId": None},
                "models": ["test-model"]
            }
        }

        # Mock completion response
        completion_response = Mock()
        completion_response.status_code = 200
        completion_response.json.return_value = {
            "choices": [{"message": {"content": "Hello user!"}}]
        }

        # Sequence of calls: search, create, load, completion
        self.mock_httpx_client.get.side_effect = [
            search_response, # search
            details_response, # load details
        ]

        self.mock_httpx_client.post.side_effect = [
            create_response, # create
            completion_response # completion
        ]

        response = await self.client.chat("Hello", "New Chat")

        self.assertIsNotNone(response)
        self.assertEqual(response["response"], "Hello user!")

class TestAsyncClientInitialization(unittest.TestCase):
    def test_kwargs_passing(self):
        """Test that kwargs are passed to httpx.AsyncClient."""
        base_url = "http://localhost:3000"
        token = "test_token"
        default_model = "test-model"

        with patch('httpx.AsyncClient') as mock_client_cls:
            # Test 1: Custom verify parameter
            client = AsyncOpenWebUIClient(base_url, token, default_model, verify=False, custom_param="value")
            call_kwargs = mock_client_cls.call_args[1]
            self.assertIn("verify", call_kwargs)
            self.assertEqual(call_kwargs["verify"], False)
            self.assertIn("custom_param", call_kwargs)
            self.assertEqual(call_kwargs["custom_param"], "value")

            # Test 2: Headers merging
            client = AsyncOpenWebUIClient(base_url, token, default_model, headers={"X-Custom": "TestHeader"})
            call_kwargs = mock_client_cls.call_args[1]
            headers = call_kwargs["headers"]
            self.assertIn("X-Custom", headers)
            self.assertEqual(headers["X-Custom"], "TestHeader")
            self.assertIn("Authorization", headers) # Auth should persist

            # Test 3: Transport override
            custom_transport = Mock()
            client = AsyncOpenWebUIClient(base_url, token, default_model, transport=custom_transport)
            call_kwargs = mock_client_cls.call_args[1]
            self.assertEqual(call_kwargs["transport"], custom_transport)

if __name__ == '__main__':
    unittest.main()
