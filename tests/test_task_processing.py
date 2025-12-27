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

    def test_enhanced_prompt_contains_key_findings(self):
        """Test that the enhanced prompt includes Key Findings section."""
        prompt = self.client._chat_manager._get_task_processing_prompt()
        
        # Check for Key Findings section
        self.assertIn("Key Findings", prompt)
        self.assertIn("Knowledge Accumulation", prompt)
        self.assertIn("[From tool", prompt)
        
    def test_enhanced_prompt_contains_options_guidance(self):
        """Test that the enhanced prompt includes guidance for multiple options."""
        prompt = self.client._chat_manager._get_task_processing_prompt()
        
        # Check for options handling guidance
        self.assertIn("Options:", prompt)
        self.assertIn("multiple solution options", prompt)

    def test_detect_options_in_response_with_valid_options(self):
        """Test detection of multiple options in AI response."""
        response_text = """Thought:
**Key Findings:**
- [From search] Found 3 possible approaches

**Options:**
1. [Direct API]: Use the direct API call method
2. [Batch Processing]: Process items in batches for efficiency
3. [Async Method]: Use async/await for better performance

I will proceed with the best option.

Action:
```json
{"tool": "test", "args": {}}
```"""
        
        options = self.client._chat_manager._detect_options_in_response(response_text)
        
        self.assertIsNotNone(options)
        self.assertEqual(len(options), 3)
        self.assertEqual(options[0]["number"], "1")
        self.assertEqual(options[0]["label"], "Direct API")

    def test_detect_options_in_response_without_options(self):
        """Test that no options are detected when none exist."""
        response_text = """Thought:
I will solve this problem step by step.

Action:
```json
{"tool": "calculator", "args": {"operation": "add", "a": 1, "b": 2}}
```"""
        
        options = self.client._chat_manager._detect_options_in_response(response_text)
        
        self.assertIsNone(options)

    def test_get_decision_from_model(self):
        """Test that decision model can select an option."""
        options = [
            {"number": "1", "label": "Option A", "description": "First approach"},
            {"number": "2", "label": "Option B", "description": "Second approach"},
        ]
        
        # Mock the model completion to return a decision
        self.client._chat_manager._get_model_completion = MagicMock(return_value=(
            '{"selected_option": 2, "reasoning": "Option B is more efficient"}',
            []
        ))
        
        selected = self.client._chat_manager._get_decision_from_model(
            options=options,
            context="Test context",
            decision_model_id="decision_model",
            original_question="Solve this problem"
        )
        
        self.assertEqual(selected, 2)

    def test_process_task_with_decision_model(self):
        """Test process_task with decision_model_id parameter."""
        # First response presents options, second response provides final answer
        call_count = [0]
        
        def mock_completion(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: present options
                return (
                    '''Thought:
**Options:**
1. [Method A]: Use method A
2. [Method B]: Use method B

Action:
```json
{"tool": "analyze", "args": {}}
```''',
                    []
                )
            else:
                # Subsequent calls: provide final answer
                return (
                    'Thought:\nFinal step.\nAction:\n```json\n{"final_answer": "Completed with decision model."}\n```',
                    []
                )
        
        self.client._chat_manager._get_model_completion = MagicMock(side_effect=mock_completion)
        self.client._chat_manager._get_decision_from_model = MagicMock(return_value=1)
        self.client._chat_manager._summarize_history = MagicMock(return_value="Summary")

        result = self.client.process_task(
            question="Solve with decision model.",
            model_id="test_model",
            tool_server_ids="test_tool",
            decision_model_id="decision_model_id"
        )

        # Verify decision model was called
        self.client._chat_manager._get_decision_from_model.assert_called()
        self.assertEqual(result["solution"], "Completed with decision model.")

if __name__ == '__main__':
    unittest.main()
