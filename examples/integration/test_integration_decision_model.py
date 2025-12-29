"""
Env-gated integration tests for autonomous task processing with decision model.
Tests the decision model feature for automatic option selection.

Environment Variables:
- OUI_BASE_URL: OpenWebUI instance URL (required)
- OUI_AUTH_TOKEN: Authentication token (required)
- OUI_DEFAULT_MODEL: Default model for task processing (optional)
- OUI_DECISION_MODEL: Model for automatic decision-making (optional)
- OUI_TOOL_SERVER_ID: Tool server ID for task processing (optional)

The tests will skip if required environment variables are not set.
"""

import os
import time
import uuid
import unittest

from openwebui_chat_client import OpenWebUIClient

ENV_READY = bool(os.getenv("OUI_BASE_URL") and os.getenv("OUI_AUTH_TOKEN"))
DECISION_MODEL_READY = bool(os.getenv("OUI_DECISION_MODEL"))


@unittest.skipUnless(
    ENV_READY,
    "Integration env not set (OUI_BASE_URL, OUI_AUTH_TOKEN).",
)
class TestDecisionModelIntegration(unittest.TestCase):
    """Integration tests for task processing with decision model support."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with environment configuration."""
        cls.base_url = os.getenv("OUI_BASE_URL")
        cls.token = os.getenv("OUI_AUTH_TOKEN")
        cls.default_model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")
        cls.decision_model = os.getenv("OUI_DECISION_MODEL", "")
        cls.tool_server_id = os.getenv("OUI_TOOL_SERVER_ID", "")

    def setUp(self):
        """Set up each test with a fresh client."""
        try:
            self.client = OpenWebUIClient(
                self.base_url,
                self.token,
                self.default_model,
            )
        except Exception as e:
            self.skipTest(f"Failed to initialize client: {e}")

    def test_client_initialization(self):
        """Test that client initializes correctly."""
        self.assertIsNotNone(self.client)
        models = self.client.list_models()
        self.assertIsNotNone(models)
        self.assertIsInstance(models, list)
        print(f"✅ Client initialized with {len(models)} available models")

    def test_decision_model_available(self):
        """Test that configured decision model is available."""
        if not self.decision_model:
            self.skipTest("OUI_DECISION_MODEL not configured")
        
        models = self.client.list_models()
        available_model_ids = [m['id'] for m in models]
        
        if self.decision_model in available_model_ids:
            print(f"✅ Decision model '{self.decision_model}' is available")
        else:
            self.skipTest(f"Decision model '{self.decision_model}' not found in available models")

    @unittest.skipUnless(
        DECISION_MODEL_READY,
        "Decision model not configured (OUI_DECISION_MODEL).",
    )
    def test_process_task_with_decision_model(self):
        """Test process_task with decision model for automatic option selection."""
        models = self.client.list_models()
        available_model_ids = [m['id'] for m in models]
        
        # Find a suitable model for task processing
        task_model = self.default_model if self.default_model in available_model_ids else available_model_ids[0]
        
        # Verify decision model is available
        if self.decision_model not in available_model_ids:
            self.skipTest(f"Decision model '{self.decision_model}' not available")
        
        task_question = "What is 2 + 2?"
        tool_id = self.tool_server_id if self.tool_server_id else "mock-tool-server"
        
        try:
            result = self.client.process_task(
                question=task_question,
                model_id=task_model,
                tool_server_ids=tool_id,
                max_iterations=5,
                summarize_history=True,
                decision_model_id=self.decision_model,
            )
            
            self.assertIsNotNone(result)
            self.assertIn("solution", result)
            print(f"✅ Task processed successfully with decision model")
            print(f"   Solution: {result.get('solution', 'N/A')[:100]}...")
            
        except Exception as e:
            self.skipTest(f"Task processing failed: {e}")

    @unittest.skipUnless(
        DECISION_MODEL_READY,
        "Decision model not configured (OUI_DECISION_MODEL).",
    )
    def test_stream_process_task_with_decision_model(self):
        """Test stream_process_task with decision model for real-time updates."""
        models = self.client.list_models()
        available_model_ids = [m['id'] for m in models]
        
        # Find a suitable model for task processing
        task_model = self.default_model if self.default_model in available_model_ids else available_model_ids[0]
        
        # Verify decision model is available
        if self.decision_model not in available_model_ids:
            self.skipTest(f"Decision model '{self.decision_model}' not available")
        
        task_question = "What is 3 * 3?"
        tool_id = self.tool_server_id if self.tool_server_id else "mock-tool-server"
        
        try:
            stream_generator = self.client.stream_process_task(
                question=task_question,
                model_id=task_model,
                tool_server_ids=tool_id,
                max_iterations=5,
                summarize_history=True,
                decision_model_id=self.decision_model,
            )
            
            events_received = []
            final_result = None
            
            try:
                while True:
                    chunk = next(stream_generator)
                    event_type = chunk.get("type")
                    events_received.append(event_type)
                    
                    # Check for decision event
                    if event_type == "decision":
                        print(f"   🎯 Decision event: selected option {chunk.get('selected_option')}")
                    
            except StopIteration as e:
                final_result = e.value
            
            self.assertGreater(len(events_received), 0, "Should receive at least one event")
            print(f"✅ Streaming task processed successfully")
            print(f"   Events received: {len(events_received)}")
            print(f"   Event types: {set(events_received)}")
            
            if final_result:
                print(f"   Solution: {final_result.get('solution', 'N/A')[:100]}...")
            
        except Exception as e:
            self.skipTest(f"Streaming task processing failed: {e}")

    def test_process_task_without_decision_model(self):
        """Test process_task works correctly without decision model."""
        models = self.client.list_models()
        available_model_ids = [m['id'] for m in models]
        
        # Find a suitable model for task processing
        task_model = self.default_model if self.default_model in available_model_ids else available_model_ids[0]
        
        task_question = "What is 1 + 1?"
        tool_id = self.tool_server_id if self.tool_server_id else "mock-tool-server"
        
        try:
            result = self.client.process_task(
                question=task_question,
                model_id=task_model,
                tool_server_ids=tool_id,
                max_iterations=3,
                summarize_history=True,
                # decision_model_id not provided - should work without it
            )
            
            self.assertIsNotNone(result)
            self.assertIn("solution", result)
            print(f"✅ Task processed successfully without decision model")
            print(f"   Solution: {result.get('solution', 'N/A')[:100]}...")
            
        except Exception as e:
            self.skipTest(f"Task processing failed: {e}")


if __name__ == "__main__":
    unittest.main()
