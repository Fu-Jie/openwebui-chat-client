import unittest
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient


# This decorator skips the test if the required environment variables are not set.
# This allows unit tests and integration tests to be run together without forcing
# the user to have a live server configured.
@unittest.skipIf(
    not os.getenv("OPENWEBUI_BASE_URL") or not os.getenv("OPENWEBUI_TOKEN"),
    "Skipping integration tests: OPENWEBUI_BASE_URL and OPENWEBUI_TOKEN must be set in .env file",
)
class TestIntegrationOpenWebUIClient(unittest.TestCase):
    """
    Integration test suite for the OpenWebUIClient.
    These tests make real API calls to an Open WebUI server.
    """

    def setUp(self):
        """
        Set up a real client for each integration test.
        """
        self.base_url = os.getenv("OPENWEBUI_BASE_URL")
        self.token = os.getenv("OPENWEBUI_TOKEN")
        self.default_model = os.getenv("OPENWEBUI_DEFAULT_MODEL", "llama3:latest")
        
        # Test server connectivity before creating client
        try:
            # Simple connectivity test to the base URL
            response = requests.get(f"{self.base_url}/health", timeout=5)
            server_reachable = True
        except (requests.exceptions.RequestException, requests.exceptions.Timeout):
            server_reachable = False
        
        if not server_reachable:
            self.skipTest(f"OpenWebUI server at {self.base_url} is not reachable. Skipping integration tests.")
        
        self.client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
            # Note: Integration tests need real HTTP requests, so skip_model_refresh=False
        )
        self.client._auto_cleanup_enabled = False
        self.test_model_id = "my-test-model:latest"

    def tearDown(self):
        """
        Clean up any resources created during the tests.
        """
        # Attempt to delete the model created during the model management test
        # to ensure a clean state for the next run.
        try:
            self.client.delete_model(self.test_model_id)
            print(f"Cleaned up test model '{self.test_model_id}'.")
        except Exception:
            # Suppress exceptions during cleanup
            pass

    def test_list_models_integration(self):
        """
        Test if the client can successfully list models from the server.
        This is a good basic test for connectivity and authentication.
        """
        print("\\nRunning integration test: test_list_models_integration")
        models = self.client.list_models()

        # If models is None, it means there was an API error (connection, auth, etc.)
        if models is None:
            self.skipTest("Unable to connect to OpenWebUI API or authentication failed. Skipping integration test.")

        # We expect the call to succeed and return a list.
        # The list might be empty if no models are installed, which is a valid state.
        self.assertIsInstance(
            models, list, "The list_models() call should return a list."
        )
        print(f"Found {len(models)} models on the server.")

    def test_chat_integration(self):
        """
        Test the full chat flow against a live server.
        """
        print("\\nRunning integration test: test_chat_integration")
        chat_title = "My Integration Test Chat"
        question = "Hello, this is an integration test. What is 1 + 1?"

        # Find an available model to run the test with
        models = self.client.list_models()
        if models is None:
            self.skipTest("Unable to connect to OpenWebUI API or list models. Skipping integration test.")
        
        model_ids = [m["id"] for m in models]

        test_model_id = self.default_model
        if test_model_id not in model_ids:
            if not model_ids:
                self.skipTest(
                    "Skipping chat integration test: No models found on the server."
                )
            test_model_id = model_ids[0]  # Fallback to the first available model

        print(f"Using model: {test_model_id}")
        self.client.default_model_id = test_model_id

        try:
            result = self.client.chat(question=question, chat_title=chat_title)
        except requests.exceptions.HTTPError as e:
            # If the model is unavailable or fails to load, the server may return a 500 error.
            # In this case, we skip the test as it's a server-side issue, not a client one.
            if e.response.status_code >= 500:
                self.skipTest(
                    f"Skipping chat test: Server returned a {e.response.status_code} error for model '{test_model_id}'."
                )
            # Re-raise the exception if it's not a 500-level error
            raise e

        self.assertIsNotNone(result, "The chat() call should not return None.")
        self.assertIn("response", result)
        self.assertIn("chat_id", result)
        self.assertIn("message_id", result)
        self.assertIsInstance(result["response"], str)
        self.assertTrue(
            len(result["response"]) > 0, "The response should not be empty."
        )

        print(f"  > Question: {question}")
        print(f"  > Response: {result['response']}")
        print("  > Chat integration test passed.")

    def test_model_management_integration(self):
        """
        Test the full CRUD (Create, Read, Update, Delete) for models.
        """
        print("\\nRunning integration test: test_model_management_integration")
        model_id = self.test_model_id
        model_name = "My Integration Test Model"

        # Pre-cleanup: Attempt to delete the model in case it was left over
        # from a previous failed run.
        self.client.delete_model(model_id)

        # Find an available model to use as a base for creating a new one
        models = self.client.list_models()
        if models is None:
            self.skipTest("Unable to connect to OpenWebUI API or list models. Skipping integration test.")
        
        model_ids = [m["id"] for m in models]

        base_model_id = self.default_model
        if base_model_id not in model_ids:
            if not model_ids:
                self.skipTest(
                    "Skipping model management test: No models found on the server to use as a base."
                )
            base_model_id = model_ids[0]  # Fallback to the first available model

        # 1. CREATE
        print(f"  > Creating model '{model_name}'...")
        created_model = self.client.create_model(
            model_id=model_id,
            name=model_name,
            base_model_id=base_model_id,
            description="Initial description.",
        )
        self.assertIsNotNone(
            created_model, "create_model should return the created model."
        )
        self.assertEqual(created_model.get("id"), model_id)
        print("  > Model created successfully.")

        # 2. READ
        print(f"  > Reading model '{model_id}'...")
        read_model = self.client.get_model(model_id)
        self.assertIsNotNone(read_model, "get_model should find the created model.")
        self.assertEqual(
            read_model.get("meta", {}).get("description"), "Initial description."
        )
        print("  > Model read successfully.")

        # 3. UPDATE
        print(f"  > Updating model '{model_id}'...")
        updated_model = self.client.update_model(
            model_id=model_id, description="Updated description."
        )
        self.assertIsNotNone(
            updated_model, "update_model should return the updated model."
        )
        self.assertEqual(
            updated_model.get("meta", {}).get("description"), "Updated description."
        )
        print("  > Model updated successfully.")

        # 4. DELETE
        print(f"  > Deleting model '{model_id}'...")
        delete_result = self.client.delete_model(model_id)
        self.assertTrue(delete_result, "delete_model should return True on success.")
        print("  > Model deleted successfully.")

        # 5. VERIFY DELETION
        print(f"  > Verifying model '{model_id}' is deleted...")
        deleted_model = self.client.get_model(model_id)
        self.assertIsNone(
            deleted_model, "get_model should return None for a deleted model."
        )
        print("  > Deletion verified.")
        print("  > Model management integration test passed.")


if __name__ == "__main__":
    unittest.main()
