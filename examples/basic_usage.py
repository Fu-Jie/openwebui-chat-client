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
DEFAULT_MODEL = "gpt-4.1"
PARALLEL_MODELS = ["gpt-4.1", "gemini-2.5-flash"]


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
    responses = client.parallel_chat(
        question="What are the top 3 benefits of using Python for data science?",
        chat_title="Python for Data Science",
        model_ids=PARALLEL_MODELS,
        folder_name="Technical Questions",
    )

    # 3. Print the responses from each model
    if responses:
        print("\n" + "=" * 25 + " Model Responses " + "=" * 25)
        for model, content in responses.items():
            print(f"\n🤖 [{model}'s Response]:\n{content}")
        print("\n" + "=" * 67)

    logging.info("\n🎉 Demo completed. Please check your Open WebUI interface.")


if __name__ == "__main__":
    run_demo()
