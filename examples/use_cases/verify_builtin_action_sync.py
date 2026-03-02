import os
import sys
import logging
import time
import uuid

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
from openwebui_chat_client import OpenWebUIClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("BuiltinSyncTest")

def main():
    load_dotenv()
    base_url = os.getenv("OUI_BASE_URL", "http://localhost:3000")
    token = os.getenv("OUI_AUTH_TOKEN")
    model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4o")

    if not token:
        logger.error("❌ OUI_AUTH_TOKEN not set")
        return

    # Initialize client
    client = OpenWebUIClient(base_url=base_url, token=token, default_model_id=model)
    logger.info("🚀 Client initialized")

    # Use a unique title
    test_title = f"Built-in Sync Test {str(uuid.uuid4())[:8]}"

    try:
        # 1. Initiating Chat
        logger.info(f"
💬 Step 1: Initiating chat '{test_title}'...")
        result = client.chat(
            question="Tell me a detailed story about a space explorer discovering a new planet.",
            chat_title=test_title
        )

        if not result or not result.content:
            logger.error("❌ Failed to get response")
            return

        chat_id = result.chat_id
        message_id = result.message_id
        logger.info(f"✅ Chat completed. Content Length: {len(result.content)}")

        # 2. Triggering Action (The SDK now handles everything internally!)
        logger.info(f"
⚡ Step 2: Triggering 'smart_mind_map' via BUILT-IN synchronization...")
        
        # Notice: We only pass the IDs. The SDK handles context, spoofing, and DB syncing.
        action_result = client.trigger_action(
            action_id="smart_mind_map",
            chat_id=chat_id,
            message_id=message_id,
            params={"version": "0.1.0"} # Still useful to force direct data return
        )

        if action_result and action_result.status:
            logger.info(f"🎉 SUCCESS! The action was triggered and synchronized automatically.")
            logger.info(f"🏁 Please refresh your browser and check chat: '{test_title}'")
        else:
            logger.error("❌ Action execution reported failure.")

    except Exception as e:
        logger.error(f"❌ Error during test: {e}")

if __name__ == "__main__":
    main()
