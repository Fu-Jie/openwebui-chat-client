"""
Example of using the AsyncOpenWebUIClient for a basic asynchronous chat.
"""

import asyncio
import logging
import sys
from openwebui_chat_client import AsyncOpenWebUIClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Replace with your OpenWebUI instance details
# You can also use environment variables (e.g., os.getenv("OUI_BASE_URL"))
BASE_URL = "http://localhost:8080"
# Replace with your bearer token
TOKEN = "your_bearer_token_here"
DEFAULT_MODEL = "llama3"


async def main():
    """
    Main asynchronous function to run the chat client example.
    """
    logging.info("Initializing async client...")

    try:
        # It's best practice to use the async client as a context manager
        async with await AsyncOpenWebUIClient.create(
            base_url=BASE_URL,
            token=TOKEN,
            default_model_id=DEFAULT_MODEL
        ) as client:

            logging.info(f"Client initialized. Available models: {client.models.available_model_ids}")

            question = "Hello! In three sentences, what is asynchronous programming?"
            chat_title = "Async Test Chat"

            logging.info(f"Sending question: '{question}' to chat: '{chat_title}'")

            # Call the chat method from the chat manager
            result = await client.chat.chat(
                question=question,
                chat_title=chat_title
            )

            if result and result.get('response'):
                logging.info("--- Response Received ---")
                logging.info(f"Response: {result.get('response')}")
                logging.info(f"Chat ID: {result.get('chat_id')}")
                logging.info(f"Message ID: {result.get('message_id')}")
                logging.info("-------------------------")
                logging.info("✅ Async chat test successful!")
            else:
                logging.error("❌ Failed to get a valid response from the server.")
                sys.exit(1)

    except Exception as e:
        logging.error(f"❌ An error occurred during the async chat test: {e}")
        logging.error(
            "Please ensure your OpenWebUI server is running at the specified BASE_URL "
            "and that your OUI_AUTH_TOKEN is correct."
        )
        sys.exit(1)


if __name__ == "__main__":
    # To run this example, you would typically have a .env file or export the
    # environment variables OUI_BASE_URL and OUI_TOKEN
    # For this example, please replace the placeholder values at the top of the file.

    # Check if placeholders are still present
    if "your_bearer_token_here" in TOKEN or "localhost" in BASE_URL:
        print("="*80)
        print("⚠️  PLEASE CONFIGURE YOUR DETAILS IN THE SCRIPT  ⚠️")
        print(f"Edit the file 'examples/async/basic_async_chat.py' and replace the placeholder values for BASE_URL and TOKEN.")
        print("="*80)
    else:
        asyncio.run(main())
