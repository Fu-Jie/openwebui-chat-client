import os
import sys
import logging
import time
import uuid
from typing import List, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from dotenv import load_dotenv
from openwebui_chat_client import OpenWebUIClient
from openwebui_chat_client.models import ChatResponse, Function, ActionResult

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    # Load environment variables
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

    # Use a unique title for this silent test
    unique_suffix = str(uuid.uuid4())[:8]
    test_title = f"Silent AI History Test {unique_suffix}"

    try:
        # 1. Start a chat with a request for a detailed answer
        logger.info(f"\n💬 Step 1: Initiating silent chat '{test_title}'...")
        result: ChatResponse = client.chat(
            question="Provide a very comprehensive overview of the history of Artificial Intelligence from 1950 to today.",
            chat_title=test_title
        )

        if not result or not result.content:
            logger.error("❌ Failed to get chat response")
            return

        content_len = len(result.content)
        print(f"🤖 Assistant ({content_len} chars): {result.content[:200]}...")
        
        chat_id = result.chat_id
        message_id = result.message_id
        logger.info(f"✅ Chat completed. Chat ID: {chat_id}")

        # --- Fully Automatic: Wait for DB stabilization ---
        logger.info("⏳ Waiting 2 seconds for server-side state to stabilize...")
        time.sleep(2)

        # 2. Get the full chat history context
        logger.info("\n📚 Fetching chat history for context...")
        chat_details = client.get_chat(chat_id)
        messages = []
        if chat_details and chat_details.chat and chat_details.chat.history:
            messages_dict = chat_details.chat.history.messages
            # Convert objects to dicts
            messages = [m.model_dump() for m in messages_dict.values()]

        # 3. Locate the Smart Mind Map action
        logger.info("\n🔍 Step 2: Locating 'Smart Mind Map' action...")
        target_action_id = "smart_mind_map"
        
        # 4. Trigger the action (Silent Sync Mode)
        logger.info(f"\n⚡ Step 3: Triggering '{target_action_id}' (Silent Mode)...")
        
        # Spoofing version to encourage direct data return
        extra_params = {
            "messages": messages,
            "version": "0.1.0"
        }

        action_result: ActionResult = client.trigger_action(
            action_id=target_action_id,
            chat_id=chat_id,
            message_id=message_id,
            params=extra_params
        )

        if action_result and action_result.status:
            logger.info(f"✅ Action triggered successfully!")
            logger.info("🛠 Verifying persistence...")
            
            # Re-fetch to confirm
            final_check = client.get_chat(chat_id)
            if final_check and final_check.chat and final_check.chat.history:
                msg = final_check.chat.history.messages.get(message_id)
                if msg and msg.embeds:
                    logger.info(f"🎉 SUCCESS! Found {len(msg.embeds)} embeds in the message.")
                else:
                    logger.warning("⚠️ No embeds found in the final check. This Action might be pure real-time.")
            
            logger.info(f"\n🏁 Test Complete. Please check your browser for: '{test_title}'")
        else:
            logger.error("❌ Action trigger failed.")

    except Exception as e:
        logger.error(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
