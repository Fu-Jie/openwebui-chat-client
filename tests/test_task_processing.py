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
            # Mock the internal client/manager methods that make network calls
            self.client._base_client._parent_client = self.client
            self.client._chat_manager.base_client._parent_client = self.client
            self.client._find_or_create_chat_by_title = MagicMock(return_value="test_chat_id")
            self.client._chat_manager._find_or_create_chat_by_title = MagicMock(return_value="test_chat_id")
            self.client.chat_id = "test_chat_id"

    def test_process_task_success(self):
        """Test the process_task function for a successful multi-step task."""
        # Mock the chat method to simulate a two-step process
        self.client._chat_manager.chat = MagicMock(side_effect=[
            {"response": "First step is to use the tool."},
            {"response": "Final Answer: The task is complete."},
        ])

        result = self.client.process_task(
            question="Solve this complex problem.",
            model_id="test_model",
            tool_server_ids="test_tool"
        )

        self.assertEqual(self.client._chat_manager.chat.call_count, 2)
        self.assertIn("solution", result)
        self.assertEqual(result["solution"], "Final Answer: The task is complete.")
        self.assertEqual(len(result["conversation_history"]), 2)

    def test_process_task_max_iterations(self):
        """Test that process_task stops after max_iterations."""
        # Mock the chat method to always return an intermediate step
        self.client._chat_manager.chat = MagicMock(return_value={"response": "Still working..."})

        result = self.client.process_task(
            question="Solve this complex problem.",
            model_id="test_model",
            tool_server_ids="test_tool",
            max_iterations=3
        )

        self.assertEqual(self.client._chat_manager.chat.call_count, 3)
        self.assertEqual(result["solution"], "Max iterations reached.")

    def test_stream_process_task_success(self):
        """Test the stream_process_task function for a successful multi-step task."""
        # This needs to be a function that returns a new generator each time
        def get_stream_chat_side_effect():
            call_count = 0
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    def gen1():
                        yield "Thinking... "
                        yield "tool call needed."
                    return gen1()
                else:
                    def gen2():
                        yield "Final Answer: "
                        yield "Streamed task complete."
                    return gen2()
            return MagicMock(side_effect=side_effect)

        self.client._chat_manager.stream_chat = get_stream_chat_side_effect()

        full_response = []
        for chunk in self.client.stream_process_task(
            question="Solve this complex problem.",
            model_id="test_model",
            tool_server_ids="test_tool"
        ):
            full_response.append(chunk)

        self.assertEqual(self.client._chat_manager.stream_chat.call_count, 2)

        iteration_starts = [r for r in full_response if r.get("type") == "iteration_start"]
        self.assertEqual(len(iteration_starts), 2)

        content_chunks = [r.get("content", "") for r in full_response if r.get("type") == "content"]
        final_content = "".join(content_chunks)
        self.assertIn("Final Answer: Streamed task complete.", final_content)

        completion_events = [r for r in full_response if r.get("type") == "complete"]
        self.assertEqual(len(completion_events), 1)
        self.assertIn("solution", completion_events[0]["result"])

if __name__ == '__main__':
    unittest.main()
