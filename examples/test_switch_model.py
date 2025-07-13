# examples/test_switch_model.py

import logging
import os
from dotenv import load_dotenv
from typing import Union, List
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from openwebui_chat_client import OpenWebUIClient

# Load environment variables from a .env file if it exists
load_dotenv()

BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")

# *** Models for Testing ***
DEFAULT_MODEL = "gpt-4.1" # Replace with a model available in your Open WebUI instance
ANOTHER_MODEL = "gemini-2.5-flash" # Replace with another model available in your Open WebUI instance

# --- Configure Logging for the Application ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def test_switch_model():
    """
    Demonstrates switching the model for an existing chat using the OpenWebUIClient.
    """
    if not AUTH_TOKEN:
        logging.error(
            "🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key."
        )
        return

    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=DEFAULT_MODEL)

    # 1. Create a new chat or find an existing one
    chat_title = "Test Model Switch Chat"
    logging.info(f"--- Ensuring chat '{chat_title}' exists ---")
    # This will create the chat if it doesn't exist and load its details
    client._find_or_create_chat_by_title(chat_title)

    if not client.chat_id:
        logging.error(f"Failed to get or create chat '{chat_title}'. Cannot proceed with model switch test.")
        return

    current_chat_id = client.chat_id
    logging.info(f"Chat '{chat_title}' (ID: {current_chat_id[:8]}...) is ready.")
    logging.info(f"Initial model for chat: {client.model_id}")

    # 2. Test switching to a single new model
    logging.info(f"\n--- Attempting to switch chat '{chat_title}' to single model: {ANOTHER_MODEL} ---")
    success_single = client.switch_chat_model(current_chat_id, ANOTHER_MODEL)
    if success_single:
        logging.info(f"✅ Successfully switched chat '{chat_title}' to model '{ANOTHER_MODEL}'.")
    else:
        logging.error(f"❌ Failed to switch chat '{chat_title}' to model '{ANOTHER_MODEL}'.")

    # 3. Test switching to multiple models
    multi_models = [DEFAULT_MODEL, ANOTHER_MODEL]
    logging.info(f"\n--- Attempting to switch chat '{chat_title}' to multiple models: {multi_models} ---")
    success_multi = client.switch_chat_model(current_chat_id, multi_models)
    if success_multi:
        logging.info(f"✅ Successfully switched chat '{chat_title}' to models {multi_models}.")
    else:
        logging.error(f"❌ Failed to switch chat '{chat_title}' to models {multi_models}.")

    logging.info("\n🎉 Model switch test completed. Please verify in Open WebUI.")

if __name__ == "__main__":
    test_switch_model()
