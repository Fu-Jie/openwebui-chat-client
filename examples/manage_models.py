import os
import logging
import json
import sys

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# --- Configuration ---
# The script reads these from your environment variables.
# See instructions above on how to set them.
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# --- Test Model Details ---
# You can change these details if you want.
TEST_MODEL_ID = "d-agent-exp-designer-2"
TEST_MODEL_NAME = "My API Test Model"


def run_model_management_examples():
    """
    Demonstrates various model management operations:
    - Listing models and base models
    - Getting details of a specific model
    - Creating a new custom model
    - Updating an existing custom model
    - Deleting a custom model
    """

    if not BASE_URL or not TOKEN:
        print(
            "🛑 Error: Please set OUI_BASE_URL and OUI_AUTH_TOKEN environment variables."
        )
        print("Set OUI_DEFAULT_MODEL to specify a different default model (optional).")
        return

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    client = OpenWebUIClient(base_url=BASE_URL, token=TOKEN, default_model_id=DEFAULT_MODEL)

    # --- 1. Get Model Information ---
    print("\n" + "=" * 70)
    logging.info("Step 1: Getting Model Information")
    print("=" * 70)

    # List all available models
    print("-" * 70)
    logging.info("Listing all models available to the user...")
    models = client.list_models()
    if models:
        logging.info(f"Found {len(models)} models:")
        for model in models:
            logging.info(f"  - ID: {model.get('id')}, Name: {model.get('name')}")
    else:
        logging.warning("No models found or failed to retrieve models.")

    # List all base models
    print("-" * 70)
    logging.info("Listing all base models...")
    base_models = client.list_base_models()
    if base_models:
        logging.info(f"Found {len(base_models)} base models:")
        for bm in base_models:
            logging.info(f"  - ID: {bm.get('id')}, Name: {bm.get('name')}")
        base_model_id = base_models[0]["id"]
        logging.info(
            f"Using the first available base model for creation: '{base_model_id}'"
        )
    else:
        logging.error(
            "No base models found on the server. Cannot proceed with model creation/update tests."
        )
        return

    # Get details of a specific model (e.g., the first base model)
    if base_models:
        print("-" * 70)
        logging.info(f"Getting details for base model '{base_model_id}'...")
        specific_model_details = client.get_model(base_model_id)
        if specific_model_details:
            logging.info(f"Details for '{base_model_id}':")
            print(json.dumps(specific_model_details, indent=2))
        else:
            logging.warning(f"Could not retrieve details for model '{base_model_id}'.")

    # --- 2. Create a New Model ---
    print("\n" + "=" * 70)
    logging.info(f"Step 2: Creating a new model with ID: '{TEST_MODEL_ID}'")
    print("=" * 70)

    created_model = None
    try:
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
            logging.error("❌ Model creation failed. Aborting further tests.")
            return
    except Exception as e:
        logging.error(f"An error occurred during model creation: {e}")
        return

    # Verify the created model exists by fetching it
    print("-" * 70)
    logging.info(f"Verifying that model '{TEST_MODEL_ID}' exists after creation...")
    fetched_model = client.get_model(TEST_MODEL_ID)
    if fetched_model:
        logging.info(
            "✅ Verification successful. Model can be fetched from the server."
        )
        assert fetched_model["name"] == TEST_MODEL_NAME
        assert (
            fetched_model["meta"]["description"]
            == "This is a test model created via the Python client API."
        )
        logging.info("Model properties match the creation request.")
    else:
        logging.error("❌ Verification failed. The created model could not be fetched.")
        # We will still try to delete it in the `finally` block, just in case.
        return

    # --- 3. Update the Model ---
    print("\n" + "=" * 70)
    logging.info(f"Step 3: Updating the model '{TEST_MODEL_ID}'")
    print("=" * 70)

    updated_name = "My Updated API Test Model"
    updated_description = "This model has been updated via the Python client API."
    updated_temperature = 0.7
    updated_tags = ["test", "api-updated", "example"]

    updated_model = client.update_model(
        model_id=TEST_MODEL_ID,
        name=updated_name,
        description=updated_description,
        temperature=updated_temperature,
        tags=updated_tags,
        is_active=False,  # Deactivate the model
    )

    if updated_model:
        logging.info("✅ Model update was successful!")
        print("Server Response:")
        print(json.dumps(updated_model, indent=2))
        # Verify update
        fetched_updated_model = client.get_model(TEST_MODEL_ID)
        if fetched_updated_model:
            assert fetched_updated_model["name"] == updated_name
            assert fetched_updated_model["meta"]["description"] == updated_description
            assert fetched_updated_model["params"]["temperature"] == updated_temperature
            assert fetched_updated_model["is_active"] == False
            logging.info("✅ Verified updated properties.")
        else:
            logging.error("❌ Failed to fetch model after update for verification.")
    else:
        logging.error("❌ Model update failed.")

    # --- 4. Delete the Model (Cleanup) ---
    print("\n" + "=" * 70)
    logging.info(f"Step 4: Cleaning up by deleting the test model '{TEST_MODEL_ID}'")
    print("=" * 70)

    # First, check if the model still exists before trying to delete it.
    if client.get_model(TEST_MODEL_ID):
        deleted = client.delete_model(TEST_MODEL_ID)
        if deleted:
            logging.info("✅ Cleanup successful. Test model deleted.")
        else:
            logging.error(
                "❌ Cleanup failed. Could not delete the test model. Please delete it manually in the WebUI."
            )
    else:
        logging.info(
            "Model was not found, so no deletion is necessary. This might happen if creation failed or it was already deleted."
        )

    # Final check to confirm deletion
    print("-" * 70)
    logging.info(f"Verifying model '{TEST_MODEL_ID}' is truly gone...")
    final_check = client.get_model(TEST_MODEL_ID)
    if not final_check:
        logging.info(
            "✅ Final verification successful. Test model no longer exists on the server."
        )
    else:
        logging.error(
            "❌ Final verification failed. The model still exists after the deletion attempt."
        )
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_model_management_examples()
