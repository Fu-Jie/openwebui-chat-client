import unittest
from unittest.mock import MagicMock, patch
from openwebui_chat_client import OpenWebUIClient

class TestDeepResearch(unittest.TestCase):

    def setUp(self):
        """Set up a client instance for each test."""
        self.client = OpenWebUIClient(
            base_url="http://localhost:8080",
            token="test_token",
            default_model_id="test-model",
            skip_model_refresh=True  # Skip initial model refresh for tests
        )

    @patch('openwebui_chat_client.modules.chat_manager.ChatManager.chat')
    def test_deep_research_success_with_routing(self, mock_chat_method):
        """
        Test the successful execution of the deep_research workflow, ensuring
        a consistent chat title is used throughout.
        """
        # --- Arrange ---
        topic = "Test Topic"
        num_steps = 2
        general_models = ["gemma:7b"]
        search_models = ["duckduckgo-search"]
        expected_chat_title = f"Deep Dive: {topic}"

        # Define the sequence of responses from the mocked chat method
        mock_chat_method.side_effect = [
            # Step 1: Planning -> Chooses Search
            {"response": '{"next_question": "What is X?", "chosen_model_type": "Search-Capable"}'},
            # Step 1: Execution
            {"response": "Answer about X from search."},
            # Step 2: Planning -> Chooses General
            {"response": '{"next_question": "Summarize X.", "chosen_model_type": "General"}'},
            # Step 2: Execution
            {"response": "Summary of X from general model."},
            # Final Summary
            {"response": "This is the final report."},
        ]

        # --- Act ---
        result = self.client.deep_research(
            topic=topic,
            num_steps=num_steps,
            general_models=general_models,
            search_models=search_models
        )

        # --- Assert ---
        self.assertEqual(mock_chat_method.call_count, 5)

        # Verify that all calls used the same, consistent chat title
        for call in mock_chat_method.call_args_list:
            self.assertEqual(call.kwargs['chat_title'], expected_chat_title)

        # Check execution calls for correct model routing
        execution_call_1 = mock_chat_method.call_args_list[1]
        self.assertEqual(execution_call_1.kwargs['model_id'], search_models[0])

        execution_call_2 = mock_chat_method.call_args_list[3]
        self.assertEqual(execution_call_2.kwargs['model_id'], general_models[0])

        # Check final result
        self.assertIsNotNone(result)
        self.assertEqual(result["final_report"], "This is the final report.")
        self.assertIn(f"(using {search_models[0]})", result["research_log"][0])
        self.assertIn(f"(using {general_models[0]})", result["research_log"][1])

    @patch('openwebui_chat_client.modules.chat_manager.ChatManager.chat')
    def test_deep_research_step_failure(self, mock_chat_method):
        """
        Test that deep_research handles a failure during a research step.
        """
        # --- Arrange ---
        mock_chat_method.return_value = None

        # --- Act ---
        result = self.client.deep_research(
            topic="Failing Topic",
            num_steps=3,
            general_models=["gemma:7b"]
        )

        # --- Assert ---
        self.assertEqual(mock_chat_method.call_count, 1)
        self.assertIsNone(result)

    @patch('openwebui_chat_client.modules.chat_manager.ChatManager.chat')
    def test_deep_research_invalid_json_planning(self, mock_chat_method):
        """
        Test that deep_research handles an invalid JSON response during planning.
        """
        # --- Arrange ---
        mock_chat_method.return_value = {"response": "This is not JSON."}

        # --- Act ---
        result = self.client.deep_research(topic="Bad JSON Topic", num_steps=1, general_models=["gemma:7b"])

        # --- Assert ---
        self.assertEqual(mock_chat_method.call_count, 1)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
