import os
import unittest
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from openwebui_chat_client import AsyncOpenWebUIClient

# Load environment variables from tests/.env
load_dotenv(Path(__file__).parent / ".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAsyncChatFlow(unittest.IsolatedAsyncioTestCase):
    """Integration tests for Async chat APIs."""

    async def asyncSetUp(self):
        self.base_url = os.getenv("OPENWEBUI_BASE_URL") or os.getenv(
            "OUI_BASE_URL", "http://localhost:3000"
        )
        self.token = os.getenv("OPENWEBUI_TOKEN") or os.getenv("OUI_AUTH_TOKEN")
        self.model = os.getenv("OPENWEBUI_DEFAULT_MODEL") or os.getenv(
            "OUI_DEFAULT_MODEL", "gpt-4o"
        )

        if not self.token:
            self.skipTest(
                "OPENWEBUI_TOKEN (or OUI_AUTH_TOKEN) not set in environment or tests/.env"
            )

        self.client = AsyncOpenWebUIClient(
            base_url=self.base_url, token=self.token, default_model_id=self.model
        )
        self.chat_id = None
        self.last_user_msg_id = None

    async def asyncTearDown(self):
        if self.chat_id:
            await self.client.delete_chat(self.chat_id)
            logger.info(f"🧹 Cleaned up test chat: {self.chat_id}")
        await self.client.close()

    async def test_01_basic_chat(self):
        """chat() should create a new chat and return assistant response."""
        result = await self.client.chat(
            question="What is 1 + 1? Reply with only the number.",
            chat_title="Async Integration Test Chat",
        )
        self.assertIsNotNone(result)
        self.assertIn("2", result.content)

        # Store for follow-up tests if we were running them sequentially in one session
        # But IsolatedAsyncioTestCase runs each test separately.
        # So we either combine them or use a class-level state (risky).
        # Let's combine critical flow into one test or use a shared chat.

    async def test_full_workflow(self):
        """Test the entire conversation lifecycle: chat -> continue -> regenerate -> edit."""
        # 1. Start Chat
        chat_title = f"Async Full Workflow {int(asyncio.get_event_loop().time())}"
        res1 = await self.client.chat(
            question="What is 1+1? Reply with only number.", chat_title=chat_title
        )
        self.assertIsNotNone(res1)
        self.chat_id = res1.chat_id

        # 2. Continue Chat
        res2 = await self.client.chat(
            question="Plus 2? Reply with only number.", chat_id=self.chat_id
        )
        self.assertIsNotNone(res2)
        self.assertIn("4", res2.content)

        # History check to find message_id (using internal metadata or details)
        details = await self.client.get_chat(self.chat_id)
        # details.chat is a ChatData object, history is a ChatHistory object
        messages = details.chat.history.messages
        user_msgs = [
            m
            for m in messages.values()
            if (m.role if hasattr(m, "role") else m.get("role")) == "user"
        ]
        msg_to_edit_id = (
            user_msgs[-1].id
            if hasattr(user_msgs[-1], "id")
            else user_msgs[-1].get("id")
        )

        # 3. Regenerate
        res3 = await self.client.regenerate_message(
            chat_id=self.chat_id, parent_message_id=msg_to_edit_id
        )
        self.assertIsNotNone(res3)
        self.assertIn("4", res3.content)

        # 4. Edit message
        res4 = await self.client.edit_message(
            chat_id=self.chat_id,
            message_id=msg_to_edit_id,
            new_content="Plus 4? Reply with only number.",
        )
        self.assertIsNotNone(res4)
        self.assertIn("6", res4.content)

        # 5. Verify History Count
        details = await self.client.get_chat(self.chat_id)
        messages = details.chat.history.messages
        # 1+1 (U), 2 (A), Plus 2 (U), 4 (A), Plus 2 (U-Regen, but regen actually adds branch), ...
        # Based on logs: Final message count to persist: 8
        self.assertGreaterEqual(
            len(messages),
            4,
            "Should have at least 4 messages in tree (1+1 loop, +2 loop, regen loop, edit loop)",
        )

    async def test_stream_chat(self):
        """stream_chat() should yield chunks."""
        chunks = []
        async for chunk in self.client.stream_chat(
            question="Say 'hello'", model_id=self.model
        ):
            chunks.append(chunk)

        self.assertTrue(len(chunks) > 0)
        full_text = "".join(chunks)
        self.assertIn("hello", full_text.lower())
