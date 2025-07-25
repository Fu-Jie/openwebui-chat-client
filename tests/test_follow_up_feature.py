import unittest
import json  # Added this import
from unittest.mock import MagicMock, patch, call
from openwebui_chat_client import OpenWebUIClient


class TestFollowUpFeature(unittest.TestCase):

    def setUp(self):
        """Set up a client instance before each test."""
        # Patch list_models during initialization to prevent network call
        with patch.object(
            OpenWebUIClient, "list_models", return_value=["test_model", "gpt-4.1"]
        ) as mock_list_models:
            self.client = OpenWebUIClient(
                base_url="http://test.com",
                token="test_token",
                default_model_id="test_model",
            )
        self.client._auto_cleanup_enabled = False
        # Mock the session object to control API responses for other methods
        self.mock_session = MagicMock()
        self.client.session = self.mock_session

    def _mock_chat_creation_and_loading(
        self, chat_id="test_chat_id", title="Test Chat"
    ):
        """Mocks the process of creating and loading a chat."""
        # This is a bit complex because the client makes multiple calls.
        # We'll use a custom side_effect function to handle different URLs.

        def get_side_effect(*args, **kwargs):
            url = args[0]
            if "/api/v1/tasks/config" in url:
                response = MagicMock()
                response.raise_for_status.return_value = None
                response.json.return_value = {"TASK_MODEL": "gpt-4-test-task-model"}
                return response
            elif "/api/v1/chats/search" in url:
                response = MagicMock()
                response.raise_for_status.return_value = None
                response.json.return_value = []  # No existing chat found
                return response
            elif f"/api/v1/chats/{chat_id}" in url:
                response = MagicMock()
                response.raise_for_status.return_value = None
                response.json.return_value = {
                    "id": chat_id,
                    "title": title,
                    "chat": {
                        "id": chat_id,
                        "title": title,
                        "models": ["test_model"],
                        "history": {"messages": {}, "currentId": None},
                        "messages": [],
                    },
                }
                return response
            return MagicMock()  # Default mock

        self.mock_session.get.side_effect = get_side_effect

        # Mock for chat creation post
        mock_create_response = MagicMock()
        mock_create_response.raise_for_status.return_value = None
        mock_create_response.json.return_value = {"id": chat_id, "title": title}

        self.mock_session.post.side_effect = lambda *args, **kwargs: (
            mock_create_response if "/api/v1/chats/new" in args[0] else MagicMock()
        )

    @patch(
        "openwebui_chat_client.openwebui_chat_client.OpenWebUIClient._update_remote_chat"
    )
    def test_chat_with_follow_up(self, mock_update_remote_chat):
        """Test that `chat` with `enable_follow_up=True` calls the follow-up API."""
        self._mock_chat_creation_and_loading()
        mock_update_remote_chat.return_value = True

        # Mock responses for completions and follow-ups
        mock_completion_response = MagicMock()
        mock_completion_response.raise_for_status.return_value = None
        mock_completion_response.json.return_value = {
            "choices": [{"message": {"content": "This is the main answer."}}],
            "sources": [],
        }

        mock_follow_up_response = MagicMock()
        mock_follow_up_response.raise_for_status.return_value = None
        # This now mimics the complex structure with a JSON string inside 'content'
        mock_follow_up_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {"follow_ups": ["Follow-up 1", "Follow-up 2"]}
                        )
                    }
                }
            ]
        }

        # This is more robust. We define side effects based on the URL.
        original_post_side_effect = self.mock_session.post.side_effect

        def post_side_effect(*args, **kwargs):
            url = args[0]
            if "/api/chat/completions" in url:
                return mock_completion_response
            elif "/api/v1/tasks/follow_up/completions" in url:
                return mock_follow_up_response
            return original_post_side_effect(*args, **kwargs)

        self.mock_session.post.side_effect = post_side_effect

        result = self.client.chat(
            question="Test question", chat_title="Test Chat", enable_follow_up=True
        )

        # Assertions
        self.assertEqual(
            mock_update_remote_chat.call_count, 2, "Should update remote chat twice"
        )
        self.assertIn("follow_ups", result)
        self.assertEqual(result["follow_ups"], ["Follow-up 1", "Follow-up 2"])

        # Check that the follow-up API was called correctly
        # The call order is: new, completions, follow_up
        self.assertEqual(self.mock_session.post.call_count, 3)
        follow_up_call = self.mock_session.post.call_args_list[2]
        self.assertTrue(
            follow_up_call.args[0].endswith("/api/v1/tasks/follow_up/completions")
        )

        # Verify the payload for the follow-up call
        follow_up_payload = follow_up_call.kwargs["json"]
        self.assertEqual(follow_up_payload["model"], "gpt-4-test-task-model")
        self.assertFalse(follow_up_payload["stream"])
        self.assertIn("messages", follow_up_payload)

        # Check the final message has follow-ups
        last_message_id = self.client.chat_object_from_server["chat"]["history"][
            "currentId"
        ]
        last_message = self.client.chat_object_from_server["chat"]["history"][
            "messages"
        ][last_message_id]
        self.assertIn("followUps", last_message)
        self.assertEqual(last_message["followUps"], ["Follow-up 1", "Follow-up 2"])


if __name__ == "__main__":
    unittest.main()
