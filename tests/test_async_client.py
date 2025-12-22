"""
Unit tests for AsyncOpenWebUIClient and async managers.
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch
import httpx
from openwebui_chat_client import AsyncOpenWebUIClient
from openwebui_chat_client.modules.async_chat_manager import AsyncChatManager


class TestAsyncOpenWebUIClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.base_url = "http://localhost:3000"
        self.token = "test_token"
        self.default_model_id = "test-model"
        self.client = AsyncOpenWebUIClient(
            self.base_url, self.token, self.default_model_id
        )

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
                "models": ["test-model"],
            },
        }

        # Mock completion response
        completion_response = Mock()
        completion_response.status_code = 200
        completion_response.json.return_value = {
            "choices": [{"message": {"content": "Hello user!"}}]
        }

        # Sequence of calls: search, create, load, completion
        self.mock_httpx_client.get.side_effect = [
            search_response,  # search
            details_response,  # load details
        ]

        self.mock_httpx_client.post.side_effect = [
            create_response,  # create
            completion_response,  # completion
        ]

        response = await self.client.chat("Hello", "New Chat")

        self.assertIsNotNone(response)
        self.assertEqual(response["response"], "Hello user!")


class TestAsyncChatManagerBehavior(unittest.IsolatedAsyncioTestCase):
    async def test_ask_includes_rag_tools_and_images(self):
        mock_completion = Mock()
        mock_completion.status_code = 200
        mock_completion.json.return_value = {
            "choices": [{"message": {"content": "Hello async"}}]
        }

        base_client = Mock()
        base_client.default_model_id = "model-x"
        base_client.json_headers = {
            "Authorization": "Bearer token",
            "Content-Type": "application/json",
        }
        base_client._make_request = AsyncMock(return_value=mock_completion)

        manager = AsyncChatManager(base_client)

        chat_object = {
            "chat": {
                "history": {"messages": {}, "currentId": None},
                "models": [],
                "files": [],
            }
        }

        with patch.object(
            manager,
            "_handle_rag_references",
            new=AsyncMock(
                return_value=(
                    [{"type": "file", "id": "file-1"}],
                    [{"type": "file", "id": "file-1"}],
                )
            ),
        ), patch.object(
            manager,
            "_encode_image_to_base64",
            return_value="data:image/jpeg;base64,abc",
        ), patch.object(
            manager,
            "_update_remote_chat",
            new=AsyncMock(return_value=True),
        ):
            result = await manager._ask(
                "hi",
                "chat-123",
                chat_object,
                "model-x",
                image_paths=["/tmp/img.jpg"],
                rag_files=["doc.pdf"],
                rag_collections=["kb"],
                tool_ids=["tool-1"],
            )

        self.assertEqual(result["response"], "Hello async")

        base_client._make_request.assert_awaited()
        called_payload = base_client._make_request.call_args.kwargs.get("json_data")
        self.assertIn("files", called_payload)
        self.assertEqual(called_payload["tool_ids"], ["tool-1"])

        user_messages = chat_object["chat"]["history"]["messages"]
        self.assertEqual(len(user_messages), 2)  # user + assistant

        # Check stored files include RAG reference and image entry
        user_entry = next(
            msg for msg in user_messages.values() if msg["role"] == "user"
        )
        self.assertTrue(
            any(f.get("type") == "file" for f in user_entry.get("files", []))
        )
        self.assertTrue(
            any(f.get("type") == "image" for f in user_entry.get("files", []))
        )

        # Chat-level files merged
        self.assertTrue(
            any(f.get("id") == "file-1" for f in chat_object["chat"].get("files", []))
        )


class TestAsyncClientChatPassthrough(unittest.IsolatedAsyncioTestCase):
    async def test_chat_forwards_kwargs(self):
        client = AsyncOpenWebUIClient("http://localhost:3000", "token", "model")
        client._chat_manager = AsyncMock()
        await client.chat(
            "q",
            "t",
            model_id="m",
            rag_files=["f"],
            rag_collections=["kb"],
            tool_ids=["tool"],
        )

        client._chat_manager.chat.assert_awaited_with(
            "q",
            "t",
            "m",
            rag_files=["f"],
            rag_collections=["kb"],
            tool_ids=["tool"],
        )


class TestAsyncClientInitialization(unittest.TestCase):
    def test_kwargs_passing(self):
        """Test that kwargs are passed to httpx.AsyncClient."""
        base_url = "http://localhost:3000"
        token = "test_token"
        default_model = "test-model"

        with patch("httpx.AsyncClient") as mock_client_cls:
            # Test 1: Custom verify parameter
            client = AsyncOpenWebUIClient(
                base_url, token, default_model, verify=False, custom_param="value"
            )
            call_kwargs = mock_client_cls.call_args[1]
            self.assertIn("verify", call_kwargs)
            self.assertEqual(call_kwargs["verify"], False)
            self.assertIn("custom_param", call_kwargs)
            self.assertEqual(call_kwargs["custom_param"], "value")

            # Test 2: Headers merging
            client = AsyncOpenWebUIClient(
                base_url, token, default_model, headers={"X-Custom": "TestHeader"}
            )
            call_kwargs = mock_client_cls.call_args[1]
            headers = call_kwargs["headers"]
            self.assertIn("X-Custom", headers)
            self.assertEqual(headers["X-Custom"], "TestHeader")
            self.assertIn("Authorization", headers)  # Auth should persist

            # Test 3: Transport override
            custom_transport = Mock()
            client = AsyncOpenWebUIClient(
                base_url, token, default_model, transport=custom_transport
            )
            call_kwargs = mock_client_cls.call_args[1]
            self.assertEqual(call_kwargs["transport"], custom_transport)


if __name__ == "__main__":
    unittest.main()
