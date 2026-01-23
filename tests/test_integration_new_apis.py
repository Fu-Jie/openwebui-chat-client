"""
Integration tests for new APIs: get_functions, get_chat, trigger_action.

These tests require a running Open WebUI instance with:
- Environment variables set: OUI_BASE_URL, OUI_AUTH_TOKEN
- At least one chat with messages in the system
- At least one function (action/tool) registered

Usage:
    # Run integration tests
    OUI_BASE_URL=http://localhost:3000 OUI_AUTH_TOKEN=your-token \
        python -m pytest tests/test_integration_new_apis.py -v
"""

import os
import unittest
import asyncio
from typing import Optional

# Skip all tests if environment variables are not set
BASE_URL = os.getenv("OPENWEBUI_BASE_URL") or os.getenv("OUI_BASE_URL")
AUTH_TOKEN = os.getenv("OPENWEBUI_TOKEN") or os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = (
    os.getenv("OPENWEBUI_DEFAULT_MODEL") or os.getenv("OUI_DEFAULT_MODEL") or "gpt-4"
)
SKIP_INTEGRATION = not (BASE_URL and AUTH_TOKEN)
SKIP_REASON = "OPENWEBUI_BASE_URL and OPENWEBUI_TOKEN (or OUI_BASE_URL and OUI_AUTH_TOKEN) environment variables must be set"


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestGetFunctionsIntegration(unittest.TestCase):
    """Integration tests for get_functions API."""

    @classmethod
    def setUpClass(cls):
        """Set up test client."""
        from openwebui_chat_client import OpenWebUIClient

        cls.client = OpenWebUIClient(
            base_url=BASE_URL, token=AUTH_TOKEN, default_model_id=DEFAULT_MODEL
        )

    def test_get_functions_returns_list(self):
        """Test that get_functions returns a list."""
        functions = self.client.get_functions()
        self.assertIsInstance(functions, list)
        print(f"Found {len(functions)} functions")

    def test_get_functions_structure(self):
        """Test that each function has expected structure."""
        functions = self.client.get_functions()
        if functions:
            func = functions[0]
            self.assertIsNotNone(func.id)
            self.assertIsNotNone(func.name)
            self.assertIsNotNone(func.type)
            print(f"Sample function: {func.name} (ID: {func.id})")


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestGetChatIntegration(unittest.TestCase):
    """Integration tests for get_chat API."""

    @classmethod
    def setUpClass(cls):
        """Set up test client."""
        from openwebui_chat_client import OpenWebUIClient

        cls.client = OpenWebUIClient(
            base_url=BASE_URL, token=AUTH_TOKEN, default_model_id=DEFAULT_MODEL
        )
        # Get a chat ID to use for testing
        chats = cls.client.list_chats()
        cls.test_chat_id = chats[0].id if chats else None

    def test_get_chat_returns_details(self):
        """Test that get_chat returns chat details."""
        if not self.test_chat_id:
            self.skipTest("No chats available for testing")

        chat_details = self.client.get_chat(self.test_chat_id)
        self.assertIsNotNone(chat_details)
        self.assertIsNotNone(chat_details.chat)
        if chat_details.chat:
            print(f"Chat title: {chat_details.chat.title}")

    def test_get_chat_has_messages(self):
        """Test that get_chat returns messages."""
        if not self.test_chat_id:
            self.skipTest("No chats available for testing")

        chat_details = self.client.get_chat(self.test_chat_id)
        messages = {}
        if chat_details and chat_details.chat and chat_details.chat.history:
            messages = chat_details.chat.history.messages or {}
        self.assertIsInstance(messages, dict)
        print(f"Found {len(messages)} messages")

    def test_get_chat_nonexistent(self):
        """Test that get_chat returns None for nonexistent chat."""
        result = self.client.get_chat("nonexistent-chat-id-12345")
        self.assertIsNone(result)


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestTriggerActionIntegration(unittest.TestCase):
    """Integration tests for trigger_action API."""

    @classmethod
    def setUpClass(cls):
        """Set up test client."""
        from openwebui_chat_client import OpenWebUIClient

        cls.client = OpenWebUIClient(
            base_url=BASE_URL, token=AUTH_TOKEN, default_model_id=DEFAULT_MODEL
        )

        # Get a chat and message ID
        chats = cls.client.list_chats()
        cls.test_chat_id: Optional[str] = None
        cls.test_message_id: Optional[str] = None
        cls.test_action_id: Optional[str] = None

        if chats:
            cls.test_chat_id = chats[0].id
            chat_details = cls.client.get_chat(cls.test_chat_id)
            if chat_details:
                messages = {}
                if chat_details.chat and chat_details.chat.history:
                    messages = chat_details.chat.history.messages or {}
                if messages:
                    # Get the first message ID
                    first_msg = list(messages.values())[0]
                    cls.test_message_id = getattr(first_msg, "id", None) or (
                        first_msg.get("id") if isinstance(first_msg, dict) else None
                    )

        # Get an action ID
        functions = cls.client.get_functions()
        if functions:
            for func in functions:
                if func.type == "action":
                    cls.test_action_id = func.id
                    break

    def test_trigger_action_with_valid_params(self):
        """Test trigger_action with valid parameters."""
        if not all([self.test_chat_id, self.test_message_id, self.test_action_id]):
            self.skipTest(
                "Missing required test data (chat_id, message_id, or action_id)"
            )

        print(f"Triggering action '{self.test_action_id}' on chat {self.test_chat_id}")
        result = self.client.trigger_action(
            action_id=self.test_action_id,
            chat_id=self.test_chat_id,
            message_id=self.test_message_id,
        )
        # Note: Result may be None if action fails, or dict if successful
        # We mainly want to verify no exceptions are raised
        print(f"Result: {result}")

    def test_trigger_action_invalid_action_id(self):
        """Test trigger_action with invalid action ID."""
        if not all([self.test_chat_id, self.test_message_id]):
            self.skipTest("Missing required test data (chat_id or message_id)")

        result = self.client.trigger_action(
            action_id="nonexistent-action-id",
            chat_id=self.test_chat_id,
            message_id=self.test_message_id,
        )
        # Should return None for invalid action
        self.assertIsNone(result)


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestAsyncNewApisIntegration(unittest.TestCase):
    """Integration tests for async versions of new APIs."""

    def test_async_get_functions(self):
        """Test async get_functions."""
        from openwebui_chat_client import AsyncOpenWebUIClient

        async def run():
            client = AsyncOpenWebUIClient(
                base_url=BASE_URL, token=AUTH_TOKEN, default_model_id=DEFAULT_MODEL
            )
            async with client:
                functions = await client.get_functions()
                self.assertIsInstance(functions, list)
                print(f"[Async] Found {len(functions)} functions")

        asyncio.run(run())

    def test_async_get_chat(self):
        """Test async get_chat."""
        from openwebui_chat_client import AsyncOpenWebUIClient

        async def run():
            client = AsyncOpenWebUIClient(
                base_url=BASE_URL, token=AUTH_TOKEN, default_model_id=DEFAULT_MODEL
            )
            async with client:
                chats = await client.list_chats()
                if not chats:
                    self.skipTest("No chats available for testing")

                chat_id = chats[0].id
                chat_details = await client.get_chat(chat_id)
                self.assertIsNotNone(chat_details)
                if chat_details and chat_details.chat:
                    print(f"[Async] Chat title: {chat_details.chat.title}")

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
