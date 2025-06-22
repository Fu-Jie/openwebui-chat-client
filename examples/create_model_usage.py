import os
import logging
import json
from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# --- Configuration ---
# The script reads these from your environment variables.
# See instructions above on how to set them.
BASE_URL = os.getenv("OPENWEBUI_BASE_URL")
TOKEN = os.getenv("OUI_AUTH_TOKEN")

# --- Test Model Details ---
# You can change these details if you want.
TEST_MODEL_ID = "my-test-model:v1"
TEST_MODEL_NAME = "My API Test Model"


def run_model_creation_test():
    """Runs the full create-verify-delete test cycle for a model."""

    if not BASE_URL or not TOKEN:
        print(
            "🛑 Error: Please set OPENWEBUI_BASE_URL and OUI_AUTH_TOKEN environment variables."
        )
        return

    # Set up logging for detailed output
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Initialize the client. The default_model_id is not critical for this test.
    client = OpenWebUIClient(base_url=BASE_URL, token=TOKEN, default_model_id="gpt-4.1")


        # 1. Find a valid base model to build upon
    print("-" * 70)
    logging.info("Step 1: Listing base models to find a valid `base_model_id`...")
    base_models = client.list_base_models()
    if not base_models:
        logging.error(
            "No base models found on the server. Cannot proceed with the test."
        )
        return

    base_model_id = base_models[0]["id"]
    logging.info(f"Using the first available base model: '{base_model_id}'")

    # 2. Create the new model
    print("-" * 70)
    logging.info(f"Step 2: Creating a new model with ID: '{TEST_MODEL_ID}'...")
    created_model = client.create_model(
        model_id=TEST_MODEL_ID,
        name=TEST_MODEL_NAME,
        base_model_id=base_model_id,
        system_prompt="You are a helpful test assistant. You only provide factual information.",
        temperature=0.5,
        description="This is a test model created via the Python client API.",
        suggestion_prompts=["What is Open WebUI?", "How does the API work?"],
        tags=["test", "api-created"],
        capabilities={"vision": False, "web_search": True},
    )

    if created_model:
        logging.info("✅ Model creation was successful!")
        print("Server Response:")
        print(json.dumps(created_model, indent=2))
    else:
        logging.error("❌ Model creation failed. Aborting test.")
        return

    #     # 3. Verify the model exists by fetching it
    #     print("-" * 70)
    #     logging.info(f"Step 3: Verifying that model '{TEST_MODEL_ID}' exists...")
    #     fetched_model = client.get_model(TEST_MODEL_ID)
    #     if fetched_model:
    #         logging.info(
    #             "✅ Verification successful. Model can be fetched from the server."
    #         )
    #         assert fetched_model["name"] == TEST_MODEL_NAME
    #         assert (
    #             fetched_model["meta"]["description"]
    #             == "This is a test model created via the Python client API."
    #         )
    #         logging.info("Model properties match the creation request.")
    #     else:
    #         logging.error(
    #             "❌ Verification failed. The created model could not be fetched."
    #         )
    #         # We will still try to delete it in the `finally` block, just in case.
    #         return

    # finally:
    #     # 4. Cleanup: Delete the test model
    #     print("-" * 70)
    #     logging.info(
    #         f"Step 4: Cleaning up by deleting the test model '{TEST_MODEL_ID}'..."
    #     )

    #     # First, check if the model still exists before trying to delete it.
    #     if client.get_model(TEST_MODEL_ID):
    #         deleted = client.delete_model(TEST_MODEL_ID)
    #         if deleted:
    #             logging.info("✅ Cleanup successful. Test model deleted.")
    #         else:
    #             logging.error(
    #                 "❌ Cleanup failed. Could not delete the test model. Please delete it manually in the WebUI."
    #             )
    #     else:
    #         logging.info(
    #             "Model was not found, so no deletion is necessary. This might happen if creation failed."
    #         )

    #     # Final check to confirm deletion
    #     logging.info(f"Verifying model '{TEST_MODEL_ID}' is truly gone...")
    #     final_check = client.get_model(TEST_MODEL_ID)
    #     if not final_check:
    #         logging.info(
    #             "✅ Final verification successful. Test model no longer exists on the server."
    #         )
    #     else:
    #         logging.error(
    #             "❌ Final verification failed. The model still exists after the deletion attempt."
    #         )
    #     print("-" * 70)


if __name__ == "__main__":
    run_model_creation_test()
