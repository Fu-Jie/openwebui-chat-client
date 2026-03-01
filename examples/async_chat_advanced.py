import asyncio
import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openwebui_chat_client import AsyncOpenWebUIClient
from openwebui_chat_client.models import ChatResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Configuration
    base_url = os.getenv("OUI_BASE_URL", "http://localhost:3000")
    token = os.getenv("OUI_AUTH_TOKEN")
    model = os.getenv("OUI_DEFAULT_MODEL", "gpt-4o")

    if not token:
        logger.error("❌ OUI_AUTH_TOKEN not set")
        sys.exit(1)

    # Initialize the asynchronous client
    async with AsyncOpenWebUIClient(base_url=base_url, token=token, default_model_id=model) as client:
        try:
            # 1. Basic Async Chat
            logger.info("\n💬 Step 1: Basic Async Chat")
            result: ChatResponse = await client.chat(
                question="Explain quantum physics in 1 sentence.",
                chat_title="Async Science"
            )
            
            if result:
                print(f"Assistant: {result.content}")
                chat_id = result.chat_id

                # 2. Multi-turn Follow-up
                logger.info("\n📝 Step 2: Multi-turn Follow-up")
                # Use the chat_id from the first response to maintain context
                follow_up: ChatResponse = await client.chat(
                    question="Now translate that sentence into French.",
                    chat_id=chat_id
                )
                if follow_up:
                    print(f"Assistant (French): {follow_up.content}")

                # 3. Pin and Archive
                logger.info("\n📌 Step 3: Pinning & Archiving")
                await client.pin_chat(chat_id)
                logger.info(f"Chat {chat_id[:8]} pinned.")
                
                await client.archive_chat(chat_id)
                logger.info(f"Chat {chat_id[:8]} archived.")

            # 4. Search Conversations
            logger.info("\n🔍 Step 4: Searching Conversations")
            search_results = await client.search_chats(query="quantum")
            if search_results:
                print(f"Found {len(search_results)} chats containing the query.")

        except Exception as e:
            logger.error(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
