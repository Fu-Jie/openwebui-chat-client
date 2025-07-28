# examples/basic_usage.py

import logging
import os
from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv
# Load environment variables from a .env file if it exists
load_dotenv()


# --- Configuration from Environment Variables ---
# It is highly recommended to set these in your environment for security.
#
# How to set environment variables:
#
# In Linux/macOS:
#   export OUI_BASE_URL="http://localhost:3000"
#   export OUI_AUTH_TOKEN="your_api_key_here"
#
# In Windows (Command Prompt):
#   set OUI_BASE_URL="http://localhost:3000"
#   set OUI_AUTH_TOKEN="your_api_key_here"
#
# In Windows (PowerShell):
#   $env:OUI_BASE_URL="http://localhost:3000"
#   $env:OUI_AUTH_TOKEN="your_api_key_here"
#
# Alternatively, you can create a .env file and use a library like python-dotenv.

BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")

# *** Models for Testing ***
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# Parse parallel models from environment variable (comma-separated)
_parallel_models_str = os.getenv("OUI_PARALLEL_MODELS", "gpt-4.1,gemini-2.5-flash")
PARALLEL_MODELS = [model.strip() for model in _parallel_models_str.split(",") if model.strip()]


# --- Configure Logging for the Application ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def run_demo():
    """
    Demonstrates the primary multi-model functionality of the OpenWebUIClient,
    configured via environment variables.
    """
    if not AUTH_TOKEN:
        logging.error(
            "🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key."
        )
        return

    # 1. Initialize the client
    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=DEFAULT_MODEL)

    # 2. Start a multi-model parallel conversation
    logging.info("--- Starting a new multi-model parallel chat ---")
    result = client.parallel_chat(
        question="What are the top 3 benefits of using Python for data science?",
        chat_title="Python for Data Science",
        model_ids=PARALLEL_MODELS,
        folder_name="Technical Questions",
    )

    # 3. Print the entire result from the API call
    if result:
        import json
        print("\n" + "=" * 25 + " Full API Result " + "=" * 25)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n" + "=" * 67)
        # Assuming chat_id is the second element of the tuple if result is a tuple
        chat_id = result[1] if isinstance(result, tuple) and len(result) > 1 else None
        logging.info(f"Chat session saved with ID: {chat_id}")

    logging.info("\n🎉 Demo completed. Please check your Open WebUI interface.")


if __name__ == "__main__":
    run_demo()
