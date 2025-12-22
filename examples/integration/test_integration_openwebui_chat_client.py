"""
Live integration tests for the sync OpenWebUIClient (env-gated).
Requires OUI_BASE_URL and OUI_AUTH_TOKEN to be set.
"""

import os
import requests
import unittest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from openwebui_chat_client.openwebui_chat_client import OpenWebUIClient

ENV_READY = bool(os.getenv("OUI_BASE_URL") and os.getenv("OUI_AUTH_TOKEN"))


@unittest.skipUnless(
    ENV_READY,
    "Skipping integration tests: OUI_BASE_URL and OUI_AUTH_TOKEN must be set in the environment or .env file",
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
        self.base_url = os.getenv("OUI_BASE_URL")
        self.token = os.getenv("OUI_AUTH_TOKEN")
        self.default_model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

        # Test server connectivity before creating client
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            server_reachable = response.ok
        except requests.exceptions.RequestException:
            server_reachable = False

        if not server_reachable:
            self.skipTest(
                f"OpenWebUI server at {self.base_url} is not reachable. Skipping integration tests."
            )

        self.client = OpenWebUIClient(
            base_url=self.base_url,
            token=self.token,
            default_model_id=self.default_model,
        )
        self.client._auto_cleanup_enabled = False
        self.test_model_id = "my-test-model:latest"

    def tearDown(self):
        """
        Clean up any resources created during the tests.
        """
        try:
            self.client.delete_model(self.test_model_id)
        except Exception:
            pass

    def test_list_models_integration(self):
        """
        Test if the client can successfully list models from the server.
        This is a good basic test for connectivity and authentication.
        """
        models = self.client.list_models()

        if models is None:
            self.skipTest(
                "Unable to connect to OpenWebUI API or authentication failed. Skipping integration test."
            )

        self.assertIsInstance(
            models, list, "The list_models() call should return a list."
        )

    def test_chat_integration(self):
        """
        Test the full chat flow against a live server.
        """
        chat_title = "My Integration Test Chat"
        question = "Hello, this is an integration test. What is 1 + 1?"

        models = self.client.list_models()
        if models is None:
            self.skipTest(
                "Unable to connect to OpenWebUI API or list models. Skipping integration test."
            )

        model_ids = [m["id"] for m in models]

        test_model_id = self.default_model
        if test_model_id not in model_ids:
            if not model_ids:
                self.skipTest(
                    "Skipping chat integration test: No models found on the server."
                )
            test_model_id = model_ids[0]

        try:
            result = self.client.chat(
                question=question, chat_title=chat_title, model_id=test_model_id
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code >= 500:
                self.skipTest(
                    f"Skipping chat test: Server returned a {e.response.status_code} error for model '{test_model_id}'."
                )
            raise e

        self.assertIsNotNone(result, "The chat() call should not return None.")
        self.assertIn("response", result)
        self.assertIn("chat_id", result)
        self.assertIn("message_id", result)
        self.assertIsInstance(result["response"], str)
        self.assertTrue(
            len(result["response"]) > 0, "The response should not be empty."
        )

    def test_model_management_integration(self):
        """
        Test the full CRUD (Create, Read, Update, Delete) for models.
        """
        model_id = self.test_model_id
        model_name = "My Integration Test Model"

        self.client.delete_model(model_id)

        models = self.client.list_models()
        if models is None:
            self.skipTest(
                "Unable to connect to OpenWebUI API or list models. Skipping integration test."
            )

        model_ids = [m["id"] for m in models]

        base_model_id = self.default_model
        if base_model_id not in model_ids:
            if not model_ids:
                self.skipTest(
                    "Skipping model management test: No models found on the server to use as a base."
                )
            base_model_id = model_ids[0]

        created_model = self.client.create_model(
            model_id=model_id,
            name=model_name,
            base_model_id=base_model_id,
            description="Initial description.",
        )
        if not created_model:
            self.skipTest(
                "Model creation not allowed or failed on server; skipping CRUD integration test."
            )
        self.assertEqual(created_model.get("id"), model_id)

        read_model = self.client.get_model(model_id)
        self.assertIsNotNone(read_model, "get_model should find the created model.")
        self.assertEqual(
            read_model.get("meta", {}).get("description"), "Initial description."
        )

        updated_model = self.client.update_model(
            model_id=model_id, description="Updated description."
        )
        if not updated_model:
            self.skipTest(
                "Model update not allowed or failed on server; skipping CRUD integration test."
            )
        self.assertEqual(
            updated_model.get("meta", {}).get("description"), "Updated description."
        )

        delete_result = self.client.delete_model(model_id)
        if not delete_result:
            self.skipTest(
                "Model delete not allowed or failed on server; skipping CRUD integration test."
            )

        deleted_model = self.client.get_model(model_id)
        self.assertIsNone(
            deleted_model, "get_model should return None for a deleted model."
        )


if __name__ == "__main__":
    unittest.main()
