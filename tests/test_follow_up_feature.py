import unittest
import json  # Added this import
from unittest.mock import MagicMock, patch, call
from openwebui_chat_client import OpenWebUIClient


class TestFollowUpFeature(unittest.TestCase):

    def setUp(self):
        """Set up a client instance before each test."""
        self.client = OpenWebUIClient(
            base_url="http://test.com",
            token="test_token",
            default_model_id="test_model",
            skip_model_refresh=True,
        )
        self.client._auto_cleanup_enabled = False
        # Mock the session object to control API responses for other methods
        self.mock_session = MagicMock()
        self.client.session = self.mock_session
        self.client._base_client.session = self.mock_session  # Also mock the base client session

    def test_extract_json_from_content_direct_json(self):
        """Test extracting JSON from direct JSON content."""
        content = '{"follow_ups": ["Question 1", "Question 2"]}'
        result = self.client._extract_json_from_content(content)
        expected = {"follow_ups": ["Question 1", "Question 2"]}
        self.assertEqual(result, expected)

    def test_extract_json_from_content_markdown_json_block(self):
        """Test extracting JSON from markdown ```json``` blocks."""
        content = '''```json
{
  "follow_ups": [
    "如果订单表和出库单表之间还有其他关联字段，会影响我们的查询逻辑吗？",
    "在实际业务中，是否存在订单没有关联出库单的情况？如果有，如何处理这些订单？",
    "如果SignTime字段在某些出库单中为空，会影响MAX(SignTime)的计算结果吗？",
    "能否提供一个具体的订单号示例，让我看看查询结果是什么样的？",
    "除了SignTime，还有其他字段可以用来确认签收时间吗？"
  ]
}
```'''
        result = self.client._extract_json_from_content(content)
        expected = {
            "follow_ups": [
                "如果订单表和出库单表之间还有其他关联字段，会影响我们的查询逻辑吗？",
                "在实际业务中，是否存在订单没有关联出库单的情况？如果有，如何处理这些订单？",
                "如果SignTime字段在某些出库单中为空，会影响MAX(SignTime)的计算结果吗？",
                "能否提供一个具体的订单号示例，让我看看查询结果是什么样的？",
                "除了SignTime，还有其他字段可以用来确认签收时间吗？"
            ]
        }
        self.assertEqual(result, expected)

    def test_extract_json_from_content_markdown_code_block(self):
        """Test extracting JSON from markdown ``` blocks without json specifier."""
        content = '''```
{
  "follow_ups": ["Question A", "Question B"]
}
```'''
        result = self.client._extract_json_from_content(content)
        expected = {"follow_ups": ["Question A", "Question B"]}
        self.assertEqual(result, expected)

    def test_extract_json_from_content_single_backticks(self):
        """Test extracting JSON from single backtick blocks."""
        content = '`{"follow_ups": ["Question X", "Question Y"]}`'
        result = self.client._extract_json_from_content(content)
        expected = {"follow_ups": ["Question X", "Question Y"]}
        self.assertEqual(result, expected)

    def test_extract_json_from_content_mixed_text(self):
        """Test extracting JSON from content with surrounding text."""
        content = '''Here is the JSON response:
{
  "follow_ups": ["Mixed Question 1", "Mixed Question 2"]
}
Hope this helps!'''
        result = self.client._extract_json_from_content(content)
        expected = {"follow_ups": ["Mixed Question 1", "Mixed Question 2"]}
        self.assertEqual(result, expected)

    def test_extract_json_from_content_empty_content(self):
        """Test that empty content returns None."""
        result = self.client._extract_json_from_content("")
        self.assertIsNone(result)
        
        result = self.client._extract_json_from_content("   ")
        self.assertIsNone(result)
        
        result = self.client._extract_json_from_content(None)
        self.assertIsNone(result)

    def test_extract_json_from_content_invalid_json(self):
        """Test that invalid JSON content returns None."""
        content = "This is not JSON at all"
        result = self.client._extract_json_from_content(content)
        self.assertIsNone(result)
        
        content = "```json\n{invalid json}\n```"
        result = self.client._extract_json_from_content(content)
        self.assertIsNone(result)

    def test_extract_json_from_content_whitespace_handling(self):
        """Test that extra whitespace is handled properly."""
        content = '''
        
        ```json
        
        {
          "follow_ups": ["Whitespace Question"]
        }
        
        ```
        
        '''
        result = self.client._extract_json_from_content(content)
        expected = {"follow_ups": ["Whitespace Question"]}
        self.assertEqual(result, expected)

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
        "openwebui_chat_client.modules.chat_manager.ChatManager._update_remote_chat"
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
        current_id = self.client.chat_object_from_server["chat"]["history"]["currentId"]
        self.assertIsNotNone(current_id, "current_id should not be None after chat operation")
        last_message = self.client.chat_object_from_server["chat"]["history"]["messages"][current_id]
        self.assertIn("followUps", last_message)
        self.assertEqual(last_message["followUps"], ["Follow-up 1", "Follow-up 2"])

    @patch(
        "openwebui_chat_client.modules.chat_manager.ChatManager._update_remote_chat"
    )
    def test_chat_with_follow_up_markdown_format(self, mock_update_remote_chat):
        """Test that `chat` with `enable_follow_up=True` works with markdown-formatted JSON response."""
        self._mock_chat_creation_and_loading()
        mock_update_remote_chat.return_value = True

        # Mock responses for completions and follow-ups
        mock_completion_response = MagicMock()
        mock_completion_response.raise_for_status.return_value = None
        mock_completion_response.json.return_value = {
            "choices": [{"message": {"content": "This is the main answer."}}],
            "sources": [],
        }

        # Mock follow-up response with the problematic markdown format
        mock_follow_up_response = MagicMock()
        mock_follow_up_response.raise_for_status.return_value = None
        # This mimics the problematic format mentioned in the issue
        problematic_content = '''```json
{
  "follow_ups": [
    "如果订单表和出库单表之间还有其他关联字段，会影响我们的查询逻辑吗？",
    "在实际业务中，是否存在订单没有关联出库单的情况？如果有，如何处理这些订单？",
    "如果SignTime字段在某些出库单中为空，会影响MAX(SignTime)的计算结果吗？",
    "能否提供一个具体的订单号示例，让我看看查询结果是什么样的？",
    "除了SignTime，还有其他字段可以用来确认签收时间吗？"
  ]
}
```'''
        mock_follow_up_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": problematic_content
                    }
                }
            ]
        }

        # Set up side effects based on URL
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

        # Assertions - should successfully parse the follow-ups despite markdown formatting
        self.assertEqual(
            mock_update_remote_chat.call_count, 2, "Should update remote chat twice"
        )
        self.assertIn("follow_ups", result)
        expected_follow_ups = [
            "如果订单表和出库单表之间还有其他关联字段，会影响我们的查询逻辑吗？",
            "在实际业务中，是否存在订单没有关联出库单的情况？如果有，如何处理这些订单？",
            "如果SignTime字段在某些出库单中为空，会影响MAX(SignTime)的计算结果吗？",
            "能否提供一个具体的订单号示例，让我看看查询结果是什么样的？",
            "除了SignTime，还有其他字段可以用来确认签收时间吗？"
        ]
        self.assertEqual(result["follow_ups"], expected_follow_ups)

        # Check that the follow-up API was called correctly
        self.assertEqual(self.mock_session.post.call_count, 3)
        follow_up_call = self.mock_session.post.call_args_list[2]
        self.assertTrue(
            follow_up_call.args[0].endswith("/api/v1/tasks/follow_up/completions")
        )

        # Check the final message has follow-ups
        current_id = self.client.chat_object_from_server["chat"]["history"]["currentId"]
        self.assertIsNotNone(current_id, "current_id should not be None after chat operation")
        last_message = self.client.chat_object_from_server["chat"]["history"]["messages"][current_id]
        self.assertIn("followUps", last_message)
        self.assertEqual(last_message["followUps"], expected_follow_ups)


if __name__ == "__main__":
    unittest.main()
