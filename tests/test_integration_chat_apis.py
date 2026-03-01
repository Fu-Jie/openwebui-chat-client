"""
Integration tests for core chat APIs.

Verifies the end-to-end developer experience for:
  - chat()             : start a conversation and get a ChatResponse object
  - continue chat      : send a follow-up message in the same chat
  - regenerate_message : regenerate the last assistant reply
  - edit_message       : edit a user message and trigger a new completion
  - stream_chat()      : streaming chat response
  - get_chat()         : inspect chat history

Environment variables (or tests/.env):
  OPENWEBUI_BASE_URL  / OUI_BASE_URL
  OPENWEBUI_TOKEN     / OUI_AUTH_TOKEN
  OPENWEBUI_DEFAULT_MODEL / OUI_DEFAULT_MODEL  (optional, default: gpt-4.1)

Usage:
    cd /Users/fujie/app/python/oui/openwebui-client
    python -m pytest tests/test_integration_chat_apis.py -v -s
"""

import os
import time
import unittest
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE_URL = os.getenv("OPENWEBUI_BASE_URL") or os.getenv("OUI_BASE_URL")
AUTH_TOKEN = os.getenv("OPENWEBUI_TOKEN") or os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = (
    os.getenv("OPENWEBUI_DEFAULT_MODEL") or os.getenv("OUI_DEFAULT_MODEL") or "gpt-4.1"
)

SKIP_INTEGRATION = not (BASE_URL and AUTH_TOKEN)
SKIP_REASON = "OPENWEBUI_BASE_URL + OPENWEBUI_TOKEN must be set (or tests/.env)"


@unittest.skipIf(SKIP_INTEGRATION, SKIP_REASON)
class TestChatFlow(unittest.TestCase):
    """End-to-end chat flow simulating a typical developer journey."""

    CHAT_TITLE = f"Integration Test Chat {int(time.time())}"

    @classmethod
    def setUpClass(cls):
        from openwebui_chat_client import OpenWebUIClient

        cls.client = OpenWebUIClient(
            base_url=BASE_URL, token=AUTH_TOKEN, default_model_id=DEFAULT_MODEL
        )
        cls.chat_id: str | None = None
        cls.last_user_msg_id: str | None = None

    @classmethod
    def tearDownClass(cls):
        if cls.chat_id:
            ok = cls.client.delete_chat(cls.chat_id)
            if ok:
                print(f"\n🧹 Cleaned up test chat: {cls.chat_id[:8]}...")

    # ── Test 1: basic chat ────────────────────────────────────────────────────

    def test_01_basic_chat(self):
        """chat() should return a ChatResponse object with response, chat_id, message_id."""
        from openwebui_chat_client.models import ChatResponse

        result = self.client.chat(
            question="What is 1 + 1? Reply with only the number.",
            chat_title=self.CHAT_TITLE,
        )
        self.assertIsNotNone(result, "chat() must return a result")
        self.assertIsInstance(result, ChatResponse, "chat() must return ChatResponse")

        # Attribute access (not dict access)
        self.assertIsNotNone(result.content, "ChatResponse.content must not be None")
        self.assertIsNotNone(result.chat_id, "ChatResponse.chat_id must not be None")
        self.assertIsNotNone(
            result.message_id, "ChatResponse.message_id must not be None"
        )
        self.assertIsInstance(result.content, str)
        self.assertGreater(len(result.content), 0)

        TestChatFlow.chat_id = result.chat_id

        print(f"\n✅ test_01 | Response: '{result.response[:60]}'")
        print(f"   chat_id    = {result.chat_id[:8]}...")
        print(f"   message_id = {result.message_id[:8]}...")

    # ── Test 2: continue conversation ─────────────────────────────────────────

    def test_02_continue_chat(self):
        """Sending to same chat_title should reuse the same chat_id."""
        if not self.chat_id:
            self.skipTest("Depends on test_01")

        result = self.client.chat(
            question="What is 2 + 2? Reply with only the number.",
            chat_title=self.CHAT_TITLE,
        )
        self.assertIsNotNone(result)
        self.assertEqual(
            result.chat_id,
            self.chat_id,
            "Continuing by title must reuse the same chat_id",
        )

        # Find the last user message for later tests
        detail = self.client.get_chat(self.chat_id)
        self.assertIsNotNone(detail)
        chat_data = detail.chat
        # Support both ChatData (object) and ModelObject (dict-like) access
        if hasattr(chat_data, "history") and chat_data.history is not None:
            history = chat_data.history
            messages = getattr(history, "messages", {}) or {}
        else:
            history = chat_data.get("history", {}) if hasattr(chat_data, "get") else {}
            messages = (
                history.get("messages", {})
                if isinstance(history, dict) or hasattr(history, "get")
                else {}
            )

        user_msgs = {
            mid: m
            for mid, m in messages.items()
            if (m.get("role") if hasattr(m, "get") else getattr(m, "role", None))
            == "user"
        }
        self.assertGreater(len(user_msgs), 0)
        TestChatFlow.last_user_msg_id = list(user_msgs.keys())[-1]

        print(f"\n✅ test_02 | Follow-up: '{result.response[:60]}'")
        print(f"   last user msg_id = {TestChatFlow.last_user_msg_id[:8]}...")

    # ── Test 3: regenerate ────────────────────────────────────────────────────

    def test_03_regenerate_message(self):
        """regenerate_message() should produce a new assistant reply."""
        if not (self.chat_id and self.last_user_msg_id):
            self.skipTest("Depends on test_02")

        result = self.client.regenerate_message(
            chat_id=self.chat_id,
            parent_message_id=self.last_user_msg_id,
        )
        self.assertIsNotNone(result, "regenerate_message() must return a result")
        self.assertIsNotNone(result.content)
        self.assertGreater(len(result.content), 0)

        print(f"\n✅ test_03 | Regenerated: '{result.response[:60]}'")

    # ── Test 4: edit message ──────────────────────────────────────────────────

    def test_04_edit_message(self):
        """edit_message() should replace user content and trigger a new reply."""
        if not (self.chat_id and self.last_user_msg_id):
            self.skipTest("Depends on test_02")

        result = self.client.edit_message(
            chat_id=self.chat_id,
            message_id=self.last_user_msg_id,
            new_content="What is 3 + 3? Reply with only the number.",
        )
        self.assertIsNotNone(result, "edit_message() must return a result")
        self.assertIsNotNone(result.content)
        self.assertGreater(len(result.content), 0)

        print(f"\n✅ test_04 | Edit response: '{result.response[:60]}'")

    # ── Test 5: stream_chat ───────────────────────────────────────────────────

    def test_05_stream_chat(self):
        """stream_chat() should yield string chunks."""
        if not self.chat_id:
            self.skipTest("Depends on test_01")

        chunks = []
        for chunk in self.client.stream_chat(
            question="Say 'hello' exactly.",
            chat_title=self.CHAT_TITLE,
        ):
            self.assertIsInstance(chunk, str)
            chunks.append(chunk)

        full_text = "".join(chunks)
        self.assertGreater(len(full_text), 0)
        print(f"\n✅ test_05 | Streamed {len(chunks)} chunks → '{full_text[:60]}'")

    # ── Test 6: get_chat structure ────────────────────────────────────────────

    def test_06_get_chat_structure(self):
        """get_chat() should return accessible message history."""
        if not self.chat_id:
            self.skipTest("Depends on test_01")

        detail = self.client.get_chat(self.chat_id)
        self.assertIsNotNone(detail)

        chat_data = detail.chat
        self.assertIsNotNone(chat_data)

        # Support both ChatData (dataclass) and ModelObject (dict-like)
        if hasattr(chat_data, "history") and chat_data.history is not None:
            history = chat_data.history
            messages = getattr(history, "messages", {}) or {}
        else:
            history = chat_data.get("history", {}) if hasattr(chat_data, "get") else {}
            messages = history.get("messages", {}) if hasattr(history, "get") else {}

        self.assertTrue(
            hasattr(messages, "items"),
            f"messages must be dict-like, got {type(messages)}",
        )
        self.assertGreater(len(messages), 0, "Chat must have at least one message")

        for mid, msg in messages.items():
            role = (
                msg.get("role") if hasattr(msg, "get") else getattr(msg, "role", None)
            )
            self.assertIn(role, ("user", "assistant"))

        print(f"\n✅ test_06 | {len(messages)} messages in chat history")


if __name__ == "__main__":
    unittest.main(verbosity=2)
