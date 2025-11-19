import unittest
from unittest.mock import MagicMock, patch

from openwebui_chat_client import OpenWebUIClient

BASE_URL = "http://localhost:8080"
TOKEN = "test_token"
DEFAULT_MODEL = "test_model"

class TestTaskProcessing(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        with patch('requests.Session', MagicMock()):
            self.client = OpenWebUIClient(base_url=BASE_URL, token=TOKEN, default_model_id=DEFAULT_MODEL, skip_model_refresh=True)
            self.client._base_client._parent_client = self.client
            self.client._chat_manager.base_client._parent_client = self.client
            self.client._find_or_create_chat_by_title = MagicMock(return_value="test_chat_id")
            self.client._chat_manager._find_or_create_chat_by_title = MagicMock(return_value="test_chat_id")
            self.client.chat_id = "test_chat_id"

    def test_process_task_success_with_summarization(self):
        """Test process_task with history summarization."""
        self.client._chat_manager._get_model_completion = MagicMock(return_value=(
            'Thought:\nFinal step.\nAction:\n```json\n{"final_answer": "The task is complete."}\n```',
            []
        ))
        self.client._chat_manager._summarize_history = MagicMock(return_value="This is a summary.")

        result = self.client.process_task(
            question="Solve this problem.",
            model_id="test_model",
            tool_server_ids="test_tool",
            summarize_history=True
        )

        self.assertEqual(result["solution"], "The task is complete.")
        self.assertEqual(result["conversation_history"], "This is a summary.")
        self.client._chat_manager._summarize_history.assert_called_once()

    def test_stream_process_task_with_summarization(self):
        """Test stream_process_task with history summarization."""
        def mock_stream_step(*args, **kwargs):
            yield {"type": "thought", "content": "Final step."}
            yield {"type": "action", "content": {"final_answer": "Streamed task complete."}}

        self.client._chat_manager._stream_process_task_step = MagicMock(side_effect=mock_stream_step)
        self.client._chat_manager._summarize_history = MagicMock(return_value="Stream summary.")

        gen = self.client.stream_process_task(
            question="Solve this problem.",
            model_id="test_model",
            tool_server_ids="test_tool",
            summarize_history=True
        )

        final_result = None
        try:
            while True:
                next(gen)
        except StopIteration as e:
            final_result = e.value

        self.client._chat_manager._summarize_history.assert_called_once()
        self.assertIsNotNone(final_result)
        self.assertEqual(final_result["solution"], "Streamed task complete.")
        self.assertEqual(final_result["conversation_history"], "Stream summary.")

    def test_todo_list_updates_in_stream(self):
        """Test that todo_list_update events are yielded correctly."""
        def mock_stream_step(*args, **kwargs):
            # The key is that the _parse_todo_list function is looking for "Todo List:"
            yield {"type": "thought", "content": "Thought:\nTodo List:\n- [@] Step 1.\n- [ ] Step 2."}
            yield {"type": "action", "content": {"tool": "test", "args": {}}}

        self.client._chat_manager._stream_process_task_step = MagicMock(side_effect=mock_stream_step)
        self.client._chat_manager._get_model_completion = MagicMock(return_value=("Tool Result", []))


        todo_updates = []
        gen = self.client.stream_process_task(
            question="Test todo list.",
            model_id="test_model",
            tool_server_ids="test_tool"
        )

        try:
            while True:
                chunk = next(gen)
                if chunk.get("type") == "todo_list_update":
                    todo_updates.append(chunk["content"])
        except StopIteration:
            pass

        self.assertGreater(len(todo_updates), 0)
        self.assertEqual(todo_updates[0][0]["task"], "Step 1.")
        self.assertEqual(todo_updates[0][0]["status"], "in_progress")

if __name__ == '__main__':
    unittest.main()
