"""
Tests for OpenWebUIClient deep research and task processing functionality.

This module tests the advanced research and task processing methods of the OpenWebUIClient.
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

from openwebui_chat_client import OpenWebUIClient


class TestOpenWebUIClientResearch(unittest.TestCase):
    """Test cases for deep research functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "http://test.local"
        self.token = "test_token"
        self.default_model = "gpt-4"

        with patch("openwebui_chat_client.openwebui_chat_client.BaseClient"):
            self.client = OpenWebUIClient(
                self.base_url, self.token, self.default_model, skip_model_refresh=True
            )
            self.client._base_client = Mock()
            self.client._base_client.default_model_id = self.default_model
            self.client._chat_manager = Mock()

    # =============================================================================
    # Deep Research Tests
    # =============================================================================

    def test_deep_research_basic_success(self):
        """Test basic deep research with default parameters."""
        # Mock research step results
        self.client._chat_manager._perform_research_step.side_effect = [
            ("Question 1", "Answer 1", "gpt-4"),
            ("Question 2", "Answer 2", "gpt-4"),
            ("Question 3", "Answer 3", "gpt-4"),
        ]

        # Mock final report generation
        self.client._chat_manager.chat.return_value = {
            "response": "Final research report",
            "chat_id": "chat_123",
        }
        self.client._base_client.chat_id = "chat_123"

        result = self.client.deep_research(topic="AI Safety", num_steps=3)

        self.assertIsNotNone(result)
        self.assertEqual(result["topic"], "AI Safety")
        self.assertEqual(result["chat_id"], "chat_123")
        self.assertEqual(result["chat_title"], "Deep Dive: AI Safety")
        self.assertEqual(result["total_steps_completed"], 3)
        self.assertEqual(result["final_report"], "Final research report")
        self.assertEqual(len(result["research_log"]), 3)

    def test_deep_research_with_custom_title(self):
        """Test deep research with custom chat title."""
        self.client._chat_manager._perform_research_step.return_value = (
            "Question",
            "Answer",
            "gpt-4",
        )
        self.client._chat_manager.chat.return_value = {
            "response": "Report",
            "chat_id": "chat_123",
        }
        self.client._base_client.chat_id = "chat_123"

        result = self.client.deep_research(
            topic="Quantum Computing", chat_title="Custom Research Title", num_steps=1
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["chat_title"], "Custom Research Title")

    def test_deep_research_with_general_models(self):
        """Test deep research with custom general models."""
        self.client._chat_manager._perform_research_step.return_value = (
            "Question",
            "Answer",
            "claude-3",
        )
        self.client._chat_manager.chat.return_value = {
            "response": "Report",
            "chat_id": "chat_123",
        }
        self.client._base_client.chat_id = "chat_123"

        result = self.client.deep_research(
            topic="Machine Learning", num_steps=1, general_models=["claude-3", "gpt-4"]
        )

        self.assertIsNotNone(result)
        # Verify the general models were passed to research step
        call_args = self.client._chat_manager._perform_research_step.call_args
        self.assertEqual(call_args[1]["general_models"], ["claude-3", "gpt-4"])

    def test_deep_research_with_search_models(self):
        """Test deep research with search-capable models."""
        self.client._chat_manager._perform_research_step.return_value = (
            "Question",
            "Answer",
            "perplexity",
        )
        self.client._chat_manager.chat.return_value = {
            "response": "Report",
            "chat_id": "chat_123",
        }
        self.client._base_client.chat_id = "chat_123"

        result = self.client.deep_research(
            topic="Current Events", num_steps=1, search_models=["perplexity", "you.com"]
        )

        self.assertIsNotNone(result)
        call_args = self.client._chat_manager._perform_research_step.call_args
        self.assertEqual(call_args[1]["search_models"], ["perplexity", "you.com"])

    def test_deep_research_step_failure(self):
        """Test deep research when a research step fails."""
        # First step succeeds, second step fails
        self.client._chat_manager._perform_research_step.side_effect = [
            ("Question 1", "Answer 1", "gpt-4"),
            None,  # Step 2 fails
        ]

        result = self.client.deep_research(topic="Failed Research", num_steps=3)

        self.assertIsNone(result)

    def test_deep_research_final_report_failure(self):
        """Test deep research when final report generation fails."""
        self.client._chat_manager._perform_research_step.return_value = (
            "Question",
            "Answer",
            "gpt-4",
        )
        # Final report generation fails
        self.client._chat_manager.chat.return_value = None
        self.client._base_client.chat_id = "chat_123"

        result = self.client.deep_research(topic="Report Failure", num_steps=1)

        self.assertIsNotNone(result)
        self.assertEqual(
            result["final_report"], "Error: Could not generate the final report."
        )

    def test_deep_research_empty_response(self):
        """Test deep research when final report has empty response."""
        self.client._chat_manager._perform_research_step.return_value = (
            "Question",
            "Answer",
            "gpt-4",
        )
        self.client._chat_manager.chat.return_value = {"response": ""}
        self.client._base_client.chat_id = "chat_123"

        result = self.client.deep_research(topic="Empty Response", num_steps=1)

        self.assertIsNotNone(result)
        self.assertEqual(
            result["final_report"], "Error: Could not generate the final report."
        )

    def test_deep_research_no_general_models_fallback(self):
        """Test deep research falls back to default model when no general models provided."""
        self.client._chat_manager._perform_research_step.return_value = (
            "Question",
            "Answer",
            "gpt-4",
        )
        self.client._chat_manager.chat.return_value = {
            "response": "Report",
            "chat_id": "chat_123",
        }
        self.client._base_client.chat_id = "chat_123"

        result = self.client.deep_research(
            topic="Default Model Test", num_steps=1, general_models=None
        )

        self.assertIsNotNone(result)
        # Verify default model was used
        call_args = self.client._chat_manager._perform_research_step.call_args
        self.assertEqual(call_args[1]["general_models"], ["gpt-4"])

    def test_deep_research_no_search_models(self):
        """Test deep research with no search models provided."""
        self.client._chat_manager._perform_research_step.return_value = (
            "Question",
            "Answer",
            "gpt-4",
        )
        self.client._chat_manager.chat.return_value = {
            "response": "Report",
            "chat_id": "chat_123",
        }
        self.client._base_client.chat_id = "chat_123"

        result = self.client.deep_research(
            topic="No Search Models", num_steps=1, search_models=None
        )

        self.assertIsNotNone(result)
        call_args = self.client._chat_manager._perform_research_step.call_args
        self.assertEqual(call_args[1]["search_models"], [])

    # =============================================================================
    # Process Task Tests
    # =============================================================================

    def test_process_task_basic_success(self):
        """Test basic task processing with minimal parameters."""
        expected_result = {
            "solution": "Task completed",
            "conversation_history": ["msg1", "msg2"],
            "todo_list": ["item1", "item2"],
        }
        self.client._chat_manager.process_task.return_value = expected_result

        result = self.client.process_task(
            question="Solve this problem",
            model_id="gpt-4",
            tool_server_ids="tool_server_1",
        )

        self.assertEqual(result, expected_result)
        self.client._chat_manager.process_task.assert_called_once_with(
            question="Solve this problem",
            model_id="gpt-4",
            tool_server_ids="tool_server_1",
            knowledge_base_name=None,
            max_iterations=25,
            summarize_history=False,
            decision_model_id=None,
        )

    def test_process_task_with_knowledge_base(self):
        """Test task processing with knowledge base."""
        self.client._chat_manager.process_task.return_value = {"solution": "Done"}

        result = self.client.process_task(
            question="Research question",
            model_id="gpt-4",
            tool_server_ids="tool_server_1",
            knowledge_base_name="research_kb",
        )

        self.assertIsNotNone(result)
        call_args = self.client._chat_manager.process_task.call_args
        self.assertEqual(call_args[1]["knowledge_base_name"], "research_kb")

    def test_process_task_with_max_iterations(self):
        """Test task processing with custom max iterations."""
        self.client._chat_manager.process_task.return_value = {"solution": "Done"}

        result = self.client.process_task(
            question="Complex task",
            model_id="gpt-4",
            tool_server_ids="tool_server_1",
            max_iterations=50,
        )

        self.assertIsNotNone(result)
        call_args = self.client._chat_manager.process_task.call_args
        self.assertEqual(call_args[1]["max_iterations"], 50)

    def test_process_task_with_summarize_history(self):
        """Test task processing with history summarization."""
        self.client._chat_manager.process_task.return_value = {
            "solution": "Done",
            "conversation_history": "Summarized history",
        }

        result = self.client.process_task(
            question="Task with summary",
            model_id="gpt-4",
            tool_server_ids="tool_server_1",
            summarize_history=True,
        )

        self.assertIsNotNone(result)
        call_args = self.client._chat_manager.process_task.call_args
        self.assertTrue(call_args[1]["summarize_history"])

    def test_process_task_with_decision_model(self):
        """Test task processing with automatic decision model."""
        self.client._chat_manager.process_task.return_value = {"solution": "Done"}

        result = self.client.process_task(
            question="Task with decisions",
            model_id="gpt-4",
            tool_server_ids="tool_server_1",
            decision_model_id="claude-3",
        )

        self.assertIsNotNone(result)
        call_args = self.client._chat_manager.process_task.call_args
        self.assertEqual(call_args[1]["decision_model_id"], "claude-3")

    def test_process_task_with_multiple_tool_servers(self):
        """Test task processing with multiple tool servers."""
        self.client._chat_manager.process_task.return_value = {"solution": "Done"}

        result = self.client.process_task(
            question="Multi-tool task",
            model_id="gpt-4",
            tool_server_ids=["tool1", "tool2", "tool3"],
        )

        self.assertIsNotNone(result)
        call_args = self.client._chat_manager.process_task.call_args
        self.assertEqual(call_args[1]["tool_server_ids"], ["tool1", "tool2", "tool3"])

    def test_process_task_returns_none(self):
        """Test task processing when initialization fails."""
        self.client._chat_manager.process_task.return_value = None

        result = self.client.process_task(
            question="Failed task", model_id="gpt-4", tool_server_ids="tool_server_1"
        )

        self.assertIsNone(result)

    def test_process_task_all_parameters(self):
        """Test task processing with all parameters specified."""
        expected_result = {
            "solution": "Complete solution",
            "conversation_history": "Full history",
            "todo_list": ["task1", "task2"],
        }
        self.client._chat_manager.process_task.return_value = expected_result

        result = self.client.process_task(
            question="Complex task with all options",
            model_id="gpt-4",
            tool_server_ids=["tool1", "tool2"],
            knowledge_base_name="comprehensive_kb",
            max_iterations=100,
            summarize_history=True,
            decision_model_id="claude-3",
        )

        self.assertEqual(result, expected_result)
        self.client._chat_manager.process_task.assert_called_once_with(
            question="Complex task with all options",
            model_id="gpt-4",
            tool_server_ids=["tool1", "tool2"],
            knowledge_base_name="comprehensive_kb",
            max_iterations=100,
            summarize_history=True,
            decision_model_id="claude-3",
        )

    # =============================================================================
    # Stream Process Task Tests
    # =============================================================================

    def test_stream_process_task_basic(self):
        """Test streaming task processing."""
        mock_generator = iter(
            [
                {"step": 1, "content": "Step 1"},
                {"step": 2, "content": "Step 2"},
                {"solution": "Final result"},
            ]
        )
        self.client._chat_manager.stream_process_task.return_value = mock_generator

        result = self.client.stream_process_task(
            question="Stream task", model_id="gpt-4", tool_server_ids="tool_server_1"
        )

        # Consume the generator
        steps = list(result)
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0]["step"], 1)
        self.assertEqual(steps[2]["solution"], "Final result")

    def test_stream_process_task_with_all_parameters(self):
        """Test streaming task processing with all parameters."""
        mock_generator = iter([{"solution": "Done"}])
        self.client._chat_manager.stream_process_task.return_value = mock_generator

        result = self.client.stream_process_task(
            question="Stream with all params",
            model_id="gpt-4",
            tool_server_ids=["tool1", "tool2"],
            knowledge_base_name="stream_kb",
            max_iterations=75,
            summarize_history=True,
            decision_model_id="claude-3",
        )

        # Verify the generator is returned
        self.assertIsNotNone(result)
        list(result)  # Consume generator

        self.client._chat_manager.stream_process_task.assert_called_once_with(
            question="Stream with all params",
            model_id="gpt-4",
            tool_server_ids=["tool1", "tool2"],
            knowledge_base_name="stream_kb",
            max_iterations=75,
            summarize_history=True,
            decision_model_id="claude-3",
        )


if __name__ == "__main__":
    unittest.main()
